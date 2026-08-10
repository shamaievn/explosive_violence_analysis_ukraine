from extract import main as extract_data
from transform import main as transform_data
from load import main as load_data

def main():
    print('PIPELINE STARTED')

    print('Starting extraction...')
    extract_data()

    print('Starting_transformation...')
    transform_data()

    print('Starting load...')
    load_data()
    
    print('Pipeline completed successfully')


if __name__ == '__main__':
    main()