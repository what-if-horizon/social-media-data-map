
from src.inference import idStandardisation as iS


#project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
#project_root =  os.environ["PWD"]
root = '/projects/prjs2007/data_donation/ddd_processed/01_path_standardisation'
input_dir =f'{root}/011_classified_paths'
disagreements_dir = f'{root}/012_disagreements'
agreements_dir = f'{root}/013_agreements'
resolved_dir = f'{root}/014_resolved'
final_dir = f'{root}/015_final_classified_paths'

id_dir = f'{root}/00_ingest/004_largest_donation'

country_list =  ['ES', 'NL']



#print('START ', datetime.now())

def main():
    iS.process_disagreements(id_dir, input_dir, disagreements_dir, agreements_dir, resolved_dir, final_dir, country_list)

if __name__ == "__main__":
    main()

#print('FINISH ', datetime.now())




 
        