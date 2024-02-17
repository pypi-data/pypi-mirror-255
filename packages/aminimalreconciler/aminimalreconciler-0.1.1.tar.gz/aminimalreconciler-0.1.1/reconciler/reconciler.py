import csv
import argparse

class ReconciliationReport:
    def __init__(self, missing_in_target, missing_in_source, discrepancies):
        self.missing_in_target = missing_in_target
        self.missing_in_source = missing_in_source
        self.discrepancies = discrepancies

    def generate_report(self, filepath):
        try:
            with open(filepath, 'w', newline='') as file:
                writer = csv.DictWriter(file,
                                         fieldnames=
                                         ['Type', 'Record Identifier', 'Field', 'Source Value', 'Target Value'])
                writer.writeheader()
                writer.writerows(self.discrepancies)
        except FileNotFoundError:
            raise  ValueError('File not found')
        except csv.Error as e:
            raise ValueError(f'Malformed CSV file: {e}')


class Reconciler:
    def __init__(self, source_file, target_file):
        self.source_data = self._read_csv(source_file)
        self.target_data = self._read_csv(target_file)


    def _read_csv(self, file_name):
        """Read a CSV file"""
        try:
            with open(file_name, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            raise  ValueError('File not found')
        except csv.Error as e:
            raise ValueError(f'Malformed CSV file: {e}')

    def reconcile_data(self):
        """Identify records that are present in the source but missing in the target (and vice versa)."""
        discrepancies = []
        source_ids = set(record['ID'] for record in self.source_data)
        target_ids = set(record['ID'] for record in self.target_data)
        # Identify missing records in target
        missing_in_target = source_ids - target_ids
        if missing_in_target:
            for record_id in missing_in_target:
                s_record = next((record for record in self.source_data if record['ID'] == record_id), None)
                discrepancies.append({
                    'Type': 'Missing in Target',
                    'Record Identifier': s_record['ID'],
                    'Field': '',
                    'Source Value': '',
                    'Target Value': ''
                })
        # Identify missing records in source
        missing_in_source = target_ids - source_ids
        if missing_in_source:
            for record_id in missing_in_source:
                # leverage next since we may be iterating through a large dataset and it is a memory efficient approach
                # which avoids loading the entire dataset in memory
                t_record = next((record for record in self.target_data if record['ID'] == record_id), None)
                discrepancies.append({
                    'Type': 'Missing in Source',
                    'Record Identifier': t_record['ID'],
                    'Field': '',
                    'Source Value': '',
                    'Target Value': ''
                })

        # Identify field discrepancies for common records
        common_records = source_ids.intersection(target_ids)

        for record_id in common_records:
            s_record = next((record for record in self.source_data if record['ID'] == record_id), None)
            t_record = next((record for record in self.target_data if record['ID'] == record_id), None)

            if s_record and t_record:
                for field in s_record.keys():
                    if s_record[field] != t_record[field]:
                        discrepancies.append({
                            'Type': 'Field Discrepancy',
                            'Record Identifier': s_record['ID'],
                            'Field': field,
                            'Source Value': s_record[field],
                            'Target Value': t_record[field]
                        })

        return ReconciliationReport(missing_in_target, missing_in_source, discrepancies)



def main():
    """Generate reconciliation report in CSV format."""
    parser = argparse.ArgumentParser(description='Generate reconciliation report in CSV format.')
    parser.add_argument('-s','--source', help='Path to the source CSV file', required=True)
    parser.add_argument('-t', '--target', help='Path to the target CSV file', required=True)
    parser.add_argument('-o', '--output', help='Path to the output reconciliation report CSV file', required=True)
    args = parser.parse_args()

    try:
        rc = Reconciler(args.source, args.target)
        data = rc.reconcile_data()
        data.generate_report(args.output)
        print('Reconciliation completed:')
        if data.missing_in_target:
            print(f'Records in source missing in target: {len(data.missing_in_target)}')
        if data.missing_in_source:
            print(f'Records in target missing in source: {len(data.missing_in_source)}')
        if data.discrepancies:
            print(f'Discrepancies found: {len(data.discrepancies)}')
    except ValueError as e:
            print(e)

if __name__ == '__main__':
    main()
