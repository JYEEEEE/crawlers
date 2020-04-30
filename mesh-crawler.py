"""
主入口：从给定的mesh词爬取到子mesh词并入库
"""
import time

import requests

from mongodb import db

# 当前脚本的数据存入到mesh表中
table = db.mesh

# hardcode第一层mesh词
FIRST_LEVEL_MESHES = [
    {'RecordName': 'Anatomy', 'RecordUI': '', 'TreeNumber': 'A', 'HasChildren': True},
    {'RecordName': 'Organisms', 'RecordUI': '', 'TreeNumber': 'B', 'HasChildren': True},
    {'RecordName': 'Diseases', 'RecordUI': '', 'TreeNumber': 'C', 'HasChildren': True},
    {'RecordName': 'Chemicals and Drugs', 'RecordUI': '', 'TreeNumber': 'D', 'HasChildren': True},
    {'RecordName': 'Analytical, Diagnostic and Therapeutic Techniques, and Equipment',
     'RecordUI': '', 'TreeNumber': 'E', 'HasChildren': True},
    {'RecordName': 'Psychiatry and Psychology', 'RecordUI': '', 'TreeNumber': 'F', 'HasChildren': True},
    {'RecordName': 'Phenomena and Processes', 'RecordUI': '', 'TreeNumber': 'G', 'HasChildren': True},
    {'RecordName': 'Disciplines and Occupations', 'RecordUI': '', 'TreeNumber': 'H', 'HasChildren': True},
    {'RecordName': 'Anthropology, Education, Sociology, and Social Phenomena', 'RecordUI': '', 'TreeNumber': 'I',
     'HasChildren': True},
    {'RecordName': 'Technology, Industry, and Agriculture', 'RecordUI': '', 'TreeNumber': 'J', 'HasChildren': True},
    {'RecordName': 'Humanities', 'RecordUI': '', 'TreeNumber': 'K', 'HasChildren': True},
    {'RecordName': 'Information Science', 'RecordUI': '', 'TreeNumber': 'L', 'HasChildren': True},
    {'RecordName': 'Named Groups', 'RecordUI': '', 'TreeNumber': 'M', 'HasChildren': True},
    {'RecordName': 'Health Care', 'RecordUI': '', 'TreeNumber': 'N', 'HasChildren': True},
    {'RecordName': 'Publication Characteristics', 'RecordUI': '', 'TreeNumber': 'V', 'HasChildren': True},
    {'RecordName': 'Geographicals', 'RecordUI': '', 'TreeNumber': 'Z', 'HasChildren': True},
]
REQUEST_HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    # noqa
}
BASE_URL = 'https://meshb.nlm.nih.gov/api/tree/children/'


def get_children_meshes(data: list = None):
    """
    爬取所有子mesh词
    """
    for item in data:
        table.insert_one(item)
        print('insert success')
        if item.get("HasChildren"):
            time.sleep(1)
            resp = requests.get(BASE_URL + item.get('TreeNumber'), headers=REQUEST_HEADERS)
            get_children_meshes(resp.json())


get_children_meshes(FIRST_LEVEL_MESHES)

# """
# 对爬下来的数据根据RecordUI进行合并，作为爬取pubmed文章的依据
# """

# # unique_mesh_term用于去重时保存临时数据结构
# # key:'RecordUI'
# # value: item
# unique_mesh_term = {}

# with open('./crawler/unique-treenumber-mesh.txt', 'r') as f:
#     for line in f:
#         item = json.loads(line)
#         # 把TreeNumber合并之后，HasChildren这个字段就没有用了
#         item.pop('HasChildren')
#         record_ui = item.get('RecordUI')
#         if not record_ui:
#             continue

#         is_existed_ui = unique_mesh_term.get(record_ui)
#         if not is_existed_ui:
#             # 将TreeNumber转换成list
#             tree_number = item["TreeNumber"]
#             item["TreeNumber"] = [tree_number]
#             unique_mesh_term[record_ui] = item
#         else:
#             # 添加相同RecordUI不同TreeNumber的TreeNumber到item
#             unique_mesh_term[record_ui]['TreeNumber'].append(item['TreeNumber'])


# with open('./crawler/unique-id-mesh.txt', 'w') as f:
#     for mesh in FIRST_LEVEL_MESHES:
#         mesh['TreeNumber'] = [mesh['TreeNumber']]
#         mesh.pop('HasChildren')
#         f.write(json.dumps(mesh) + '\n')
#     for mesh in unique_mesh_term.values():
#         f.write(json.dumps(mesh) + '\n')
