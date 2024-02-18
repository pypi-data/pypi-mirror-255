# Job partition_by_key:00000
/path/to/partition_by_key -j 4 data_0.txt data_1.txt data_2.txt relative/path/to/output_0.txt

# Job partition_by_key:00001
/path/to/partition_by_key -j 4 data_3.txt data_4.txt data_5.txt relative/path/to/output_1.txt

# Job partition_by_key:00002
/path/to/partition_by_key -j 4 data_6.txt data_7.txt data_8.txt relative/path/to/output_2.txt

# Job aggregate_by_key:00000
/path/to/aggregate_by_key --aggregate max relative/path/to/output_0.txt

# Job aggregate_by_key:00001
/path/to/aggregate_by_key --aggregate max relative/path/to/output_1.txt

# Job aggregate_by_key:00002
/path/to/aggregate_by_key --aggregate max relative/path/to/output_2.txt

# Job count_keys:00000
/path/to/count_keys --verbose relative/path/to/output_0.txt relative/path/to/output_1.txt relative/path/to/output_2.txt combined.txt

