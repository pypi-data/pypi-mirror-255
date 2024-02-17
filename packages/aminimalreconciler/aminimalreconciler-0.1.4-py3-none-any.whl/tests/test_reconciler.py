import unittest
import csv
import os
from reconciler.reconciler import Reconciler, ReconciliationReport

class TestReconciler(unittest.TestCase):
    def setUp(self):
        # Create sample CSV files for testing
        self.source_csv_path =  'test_source.csv'
        self.target_csv_path = 'test_target.csv'
        self.output_csv_path = 'test_output.csv'

        self.create_sample_csv(self.source_csv_path, [{'ID': '1', 'Name': 'John'}, {'ID': '2', 'Name': 'Alice'}])
        self.create_sample_csv(self.target_csv_path, [{'ID': '2', 'Name': 'Alice'}, {'ID': '3', 'Name': 'Bob'}])

    def tearDown(self):
        # Remove sample CSV files after testing
        os.remove(self.source_csv_path)
        os.remove(self.target_csv_path)


    def create_sample_csv(self, file_path, data):
        with open(file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['ID', 'Name'])
            writer.writeheader()
            writer.writerows(data)

    def test_reconciliation_with_discrepancies(self):
        rc = Reconciler(self.source_csv_path, self.target_csv_path)
        report = rc.reconcile_data()

        self.assertIsInstance(report, ReconciliationReport)
        self.assertTrue(report.missing_in_target)
        self.assertTrue(report.missing_in_source)
        self.assertTrue(report.discrepancies)


    def test_report_generation(self):
        rc = Reconciler(self.source_csv_path, self.target_csv_path)
        report = rc.reconcile_data()
        report.generate_report(self.output_csv_path)

        self.assertTrue(os.path.exists(self.output_csv_path))

if __name__ == '__main__':
    unittest.main()
