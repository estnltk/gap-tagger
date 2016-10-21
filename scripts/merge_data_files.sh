DATA_DIR=$1
LINE_OFFSET=1
SAMPLE_SIZE=500
for gap_file in `find $DATA_DIR -name "*.gaps"`;
do
    for var_file in `find $DATA_DIR -name "*.var" | grep w2v`;
    do
        echo Processing $gap_file, $var_file
        python3 scripts/merge_data_files.py $gap_file $var_file $LINE_OFFSET $SAMPLE_SIZE
    done
done
