"""
解析一篇具体的文章
"""
from mongodb import db

table = db.pubmed_content


def save_content_to_mongodb(document: dict):
    """
    保存文章到数据库

    :param document:
    :return:
    """

    table.insert_one(document)
    print('insert content success.')


def parse_medline(content, record_name):
    """
    解析medline格式的文章，并存入数据库
    :param record_name:
    :param content:
    :return:
    """
    document = {'RecordName': record_name}  # 将文章解析为dict结构

    sections = []  # 段落, 举例如下: DP为一个段落，内容只有一行，TI为一个段落内容确有两行。sections用来在for循环中保存当前段落的行。
    # 例如，解析DP行时，sections=['DP', '2019 Fall']; 解析TI行时, sections=[
    #                           'TI',
    #                           'Anders Retzius and the Dental Histologists of the Mid-Nineteenth Century: Their',
    #                           'Contribution to Comparative Anatomy, Histology and Anthropology.'
    #                           ]

    """
    DP  - 2019 Fall
    TI  - Anders Retzius and the Dental Histologists of the Mid-Nineteenth Century: Their
          Contribution to Comparative Anatomy, Histology and Anthropology.
    """
    for line in content.split('\n') + ['\n']:  # + ['\n'] 补一个空行，处理文件最后没有空行的情况，避免以后最后一行数据。
        if '- ' in line:
            # line = " DP  - 2019 Fall"
            if sections:
                # 不为空时，需要处理存储在sections中的前一个段落
                # sections = [" DP  ", "2019 Fall"]
                key = sections[0].strip()  # key='DP'
                value = ' '.join(sections[1:])  # 将段落内容合并起来 value = "2019 Fall"

                if key in document:  # 检查是否又重复的字段，如果有，则合并为列表
                    if isinstance(document[key], list):  # 如果现在document[key]已经是list结构，就直接加入进去
                        document[key].append(value)
                    else:
                        document[key] = [document[key], value]
                else:  # document中没有，直接存入
                    document[key] = value

            sections = line.split('- ')  # sections = [" DP  ", "2019 Fall"]

    save_content_to_mongodb(document)


if __name__ == '__main__':
    with open('./32189624.txt', 'r') as f:
        parse_medline(f.read(), 'test')
