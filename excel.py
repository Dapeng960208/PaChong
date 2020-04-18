import xlwt

xsl_path = '夏装女短裙.xls'
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet('My Sheet')
count = 0
with open("夏装女短裙.txt", 'r', encoding='utf-8') as f:
    for line in f:
        list = line.split('|')
        if len(list) >= 4:
            company_name = list[0]
            company_member_name = list[1]
            if list[2].startswith('86'):
                company_tel = list[2][3:]
            else:
                company_tel = list[2]
            if list[3].startswith('86'):
                company_mbphone = list[3][3:]
            else:
                company_mbphone = list[3]
            worksheet.write(count, 0, company_name)
            worksheet.write(count, 1, company_mbphone)
            worksheet.write(count, 2, company_tel)
            worksheet.write(count, 3, company_member_name)
            count += 1
workbook.save(xsl_path)
print("****************%s条资料已存储完毕****************" % count)
print("****************资料存储文件名为：%s****************" % xsl_path)