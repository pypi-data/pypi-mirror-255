# -*- coding = "utf-8" -*-
# aliceCSV v0.1.0
# @Author: AliceDrop
# License: MIT License

"""
This is a module to operate csv file as a list (two-dimensional table) basing on RFC 4180.
It is easy to use ,and has no dependent libraries.
"""


def indexOfStr(target: str, string: str):
    """
    用于获取字符串string在容器字符串container出现的索引，以一个列表的形式返回所有出现位置。
    python内置了四个寻找的函数，find()返回首次出现的索引，没有则返回-1；index返回首次出现的索引，没有则会报错ValueError: substring not found
    rfind和rindex是反过来从末尾开始查找。
    count是计算出现的次数
    这些都不完全符合要求。因此写一个函数来实现。

    :param target:要查找的字符串
    :param string:被查找的字符串
    :return:list
    """
    result = []
    if target in string:
        index_to_start = 0  # 一开始从索引0开始，当找到一个则从这里开始切片。
        while 1:
            index = string[index_to_start:].find(target)  # 索引是在要找
            if index == -1:
                break
            else:
                result.append(index + index_to_start)
                index_to_start = index + index_to_start + len(target)
                # 向后切片，例如在"aa bb cc aa"中寻找aa,那么在0处找到后，就把start变成0+0+2=2，也就是在" bb cc aa bb"中寻找
                # 再在切片的7找到后，start变为7+2+2=11,这里会超出范围，但是哪怕"aa bb cc aa"[100:]都不会报错，但是[100]会。
    return result  # 如果容器中不存在要寻找的字符串，没有进入if，则返回空列表


def csvLineToList(line: str, delimiter=","):
    """
    输入一行csv的内容，识别每一列，拆分成列表
    :param line: 准备拆分成列表的csv文件的某一行，是字符串形式
    :param delimiter: 分隔符
    :return: 返回按列拆分成的列表
    """
    output_list = []
    if '"' not in line:
        output_list = line.split(delimiter)
    else:
        division_list = line.split(delimiter)  # 先把整行通过逗号分割，可能会有不应分割的（用引号括起来的部分），
        output_list = list()
        quoting = False
        cache = ""
        for item in division_list:

            if quoting:  # 如果是引文状态，那么除非是读到末尾是引号也就是 ”, ，否则都是加到缓存里面拼起来  *****
                if item[-1] == '"':
                    cache += item
                    cache = cache[1:len(cache) - 1]  # 此时cache开头和结尾是双引号，需要去掉
                    cache = cache.replace('""', '"')  # 根据RFC 4180定义第7条，引文里面的双引号要变成两个，所以解读的时候要变回一个
                    output_list.append(cache)
                    cache = ""
                    quoting = False

                else:
                    cache += item
                    cache += delimiter  # 继续补回split去掉的分隔符

            else:  # 不是引文状态：
                if len(item) == 0:
                    output_list.append("")
                elif item[0] == '"':  # 如果第一项是引号，说明开始了一个引文  *****
                    if item[-1] == '"':  # 如果最后一项是 " ，那么就是说在引文里面没有逗号，引用在这个item里面就开始并结束，所以读到的这个item就是一个列
                        item = item[1:len(item) - 1]  # 需要去掉开头和结尾的引号，提取出真正的内容
                        item = item.replace('""', '"')  # 根据RFC 4180定义第7条，引文里面的双引号要变成两个，所以解读的时候要变回一个
                        output_list.append(item)
                    else:  # 最后一项不是" ，那么就是说开始了一段引文，引文里有逗号所以拆成了几段，开quoting开始分析后面的  *****
                        quoting = True
                        cache += item
                        cache += delimiter  # 也就是说这里还是引文里面，逗号被split用掉了，所以要补上一个。
                else:  # 如果第一项不是引号，包含了 123"cde"f 之类的乱七八糟的格式，以及不含引号的最普通的项，都是直接加到列表
                    output_list.append(item)

    return output_list


def csvTo2dTable(file, delimiter=","):
    """
        将使用open打开的csv文件转为二维列表
        先进行一次遍历，把每一行去除掉末尾的换行符（如果存在）。
        :param file: 使用open()打开的csv文件
        :param delimiter: 分隔符
        :return: 二维列
    """
    data: list = file.readlines()
    for i in range(len(data)):
        row = data[i]
        if row[len(row) - 2:len(row)] == "\r\n":  # 注意！！最后两项是len()-2:len()
            row = row[:len(row) - 2]  # 因为后两位索引是len-2,len-1，这两个都舍弃，所以就是最大取到len-3，也就是[:len-2]
        elif row[-1] == "\n":
            row = row[:len(row) - 1]  # [0:len]就是从头到尾，那么[0:len-1]就是从头到倒数第二项
        # 至此去掉了末尾的换行符。
        # 之后就可以丢给分割函数了。

        data[i] = row
        data[i] = csvLineToList(data[i], delimiter)

    return data


def fixLineLength(csv_sheet):
    """
    根据RFC 4180 中csv文件的定义的第4条，每行应该含有相同数量的字段。因此对于数量对不上的要进行修复。
    对于 123"45之类的含有引号、逗号的，由于
    :param csv_sheet: 用二维表表示的csv文件
    :return:
    """
    max_length = 0
    for row in csv_sheet:  # 遍历每一行，获取最长的长度
        if len(row) > max_length:
            max_length = len(row)

    for i in range(len(csv_sheet)):
        row: list = csv_sheet[i]  # 再次遍历每一行
        if len(row) < max_length:
            for j in range(max_length - len(row)):
                row.append("")
            csv_sheet[i] = row  # 如果进入if则是需要修改，就在这里赋值，否则不变。

    return csv_sheet


def tableToCSV(sheet, output_path="output.csv", delimiter=",", sheet_encoding="utf-8", line_break="\n"):
    """
    把输入的二维列表输出为一个csv文件
    :param sheet: 一个二维列表
    :param output_path: 输出文件的路径
    :param delimiter:
    :param sheet_encoding: 输出文件使用的编码格式
    :param line_break: 输出文件使用的换行符
    """
    output = open(output_path, "w", encoding=sheet_encoding)
    for row in sheet:
        for i in range(len(row)):
            col = str(row[i])

            if '"' in col:  # 对是否要用引文进行判断，如果要就给它加上双引号
                output.write('"')  # 如果这一项里有引号，就给它加上双引号。
                output.write(col.replace('"', '""'))  # 把字段里的引号出现的
                output.write('"')
            elif "," in col or "\n" in col or delimiter in col:  # 是否有特殊符号。注意有可能分隔符不是逗号，但根据标准逗号是必须要作特殊字符的。
                output.write('"')  # 如果这一项里有逗号或是换行符，就给它加上双引号。
                output.write(col)
                output.write('"')
            else:
                output.write(col)

            if i != len(row) - 1:  # 如果不是最后一项，就加上逗号
                output.write(",")
        output.write(line_break)

    output.close()


def fixCSV(path, output_path="output.csv", origin_delimiter=",", target_delimiter=",", origin_encoding="utf-8",
           target_encoding="utf-8", target_line_break="\n"):
    origin_file = open(path, encoding=origin_encoding)
    table = csvTo2dTable(origin_file, delimiter=origin_delimiter)
    table = fixLineLength(table)
    tableToCSV(table, output_path, target_delimiter, target_encoding, target_line_break)
    origin_file.close()