# -*- coding: gbk -*-
import  sys
import time
import pglib
class a:
    def __init__(self):
        #self.con = psycopg2.connect(dbname='pds', user='postgres', password='123456', host='127.0.0.1')
        #self.cur = self.con.cursor()
        pass
    def getcon(self):
        #return self.con
        pass
    def run(self):
        return 6666
        pass
#print( demo.add( 1, 2 ) )
dd=pglib.register();
dd=pglib.pglibreadexcel("D:\\exceltest\\xlsxio-0.2.34\\Debug\\123.xlsx")
start=time.time()
print(start)
a=pglib.httpupload("http://127.0.0.1", "E:\\python3\\include\\Python.h", "456:999\r\n456:999", "456:999\r\n456:999", "969")
l=[]
l.append("456:999")
l.append("456:999")
start=time.time()
a1,b1,c1,d1=pglib.http("GET","http://127.0.0.1", [], "")
end=time.time()
print("cost %f" % (end-start))
i=pglib.genidint()
i=pglib.genidint()
l=[3,4,5]
a={1:2}
print(a.__contains__(2))
cc=[]
print(l.clear())
print(cc)
print(i)
for i in range(100):
    i=pglib.genidint4()
    #print(i)
    l.append(i)
l1=list(set(l))
print(l1.__len__())
end=time.time()
for i in range(l1.__len__()):
    if l1.__len__()!=0:
        cc.extend(l1.pop(6))
    else:
        break
    pass
print( (3.1)/3 )
print("cost %s"  %(time.time()-end))
th=[]
thradnum=0
for i in range(thradnum):
    #cc1=pglib.pglibconn("192.168.1.102",5432,'pdstest', 'pds','Fanqie@1230')
    cc1 = pglib.pglibconn("127.0.0.1", 5432, 'pds', 'postgres', '123456')
    print(cc1)
    while 1:
        if pglib.getthreadstatus(cc1)==-3:
            print(str(pglib.getMessage(cc1)))
        elif pglib.getthreadstatus(cc1)==1:
            print("login success")
            break
        elif pglib.getthreadstatus(cc1)==0:
            pass
        else:
            print(pglib.getthreadstatus(cc1))
            print(str(pglib.getMessage(cc1)))
        time.sleep(0.001)
        #print(444)
    if cc1!=-1:
        th.append(cc1)
#for i in th:
   # print(pglib.pglibselect("SELECT * FROM \"public\".\"test\" LIMIT 10",i))
l=[]
thradnum_real=len(th)
intdex=6
sqlall=""
for i in range(0):
    sql="insert into  test (tt,bb) values(4444%d,1111);" % intdex
    #sqlall=sqlall+sql
    l.append(sql)
    intdex=intdex+1
    #l.append("insert into  test (tt,bb) values(2,'你好');")
#l.append(sqlall)
print(len(l))
for i in th:
    if i!=-1:
        for x in range(1):

            status=pglib.pglibinsert(l,i)
            #print(status)
            while 1:
                #print("wait for  execute!")
                t=pglib.getthreadstatus(i)
                #print(t)
                if t == -3:
                    print(t)
                    print((pglib.getMessage(i)))
                    #exit(0)
                elif t ==2:
                    #print("execut success")
                    break
                elif t ==-2:
                    print(t)
                    print("error;;;;"+str(pglib.getMessage(i)))
                    #pglib.pglibclose(i)
                    exit(0)
                elif t==9:
                    #print("wait...")
                    pass
                elif t==1:
                    pass
                    #print(str(t)+":error:"+str(pglib.getMessage(i)))
#print(pglib.pglibselect("SELECT * FROM \"public\".\"test\" LIMIT 1",cc))
print(666)
while 0:
    time.sleep(1)
    lex = []
    for tt in th:
        print(666)
        #print("status :%d" % pglib.getthreadstatus(tt))
        if pglib.getthreadstatus(tt)==2:
            lex.append(tt)
        print(666)
    if lex.__len__()==thradnum_real:
        break
for i in th:
    pglib.pglibclose(i)
    pass
end=time.time()
cc=pglib.createpool("127.0.0.1", 5432, 'pds', 'postgres', '123456',50)
l=[]
intdex=0
for i in range(150):
    sql="insert into  test (tt,bb) values(4444%d,1111);" % intdex
    l.append(sql)
    intdex=intdex+1
print(cc)
print(l.__len__())
while 1:
    a,b=pglib.getpoolstatus(cc)
    print(a)
    print(b)
    if b==0:break
    time.sleep(2)
    pass
a=pglib.pgbatchinsert(l,cc,1000)
a, b = pglib.getpoolstatus(cc)
print(a)
print(b)
while 1:
    time.sleep(2)
    a, b = pglib.getpoolstatus(cc)
    print(a)
    print(b)
    if b == 0: break
    time.sleep(2)
print("cost %s"  %(time.time()-end))
pglib.closepgpool(cc)