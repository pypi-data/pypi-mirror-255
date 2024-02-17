from independentclusters import *
import itertools

cwd = os.getcwd()
file_path = cwd + '/Presentation_sheet.xlsx'



r = RecommendCanisterToAdd(file_name=file_path)

r.get_recommendation_to_add_canisters_truncated()