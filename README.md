# jsonpath_compare
比较常用的jsonpath库的性能,消耗内存,耗时,CPU占用等
```shell
jsonpath==0.82
jsonpath-ng==1.6.0
gjson==1.0.0
jmespath==1.0.1
```

# 生成火焰图
```shell
sudo py-spy record --function --gil --nonblocking -o profile.svg -- python main.py 
```