#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 13:59:33 2023

@author: liuzhengzuo
"""

import time
import openai
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.sparql import prepareQuery
import re

# 输入要查询的本体文件名
filename = input("请输入本体文件名：") #：/Users/liuzhengzuo/Desktop/碳酸酐酶-知识图谱/Enzyme Ontology/OntoEnzyme.owl
question = input("请输入你的问题：") #：I want to find the result sheet, which is the result sheet of a characterization, whose name is 'instant+activity_CO2'

# Start the timer
start_time = time.time()

# 声明命名空间
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# 加载.owl文件 
g = Graph()
g.parse(filename)

# 获取所有的类、对象属性、数据属性和实例
classes = g.subjects(RDF.type, OWL.Class)
object_props = g.subjects(RDF.type, OWL.ObjectProperty)
data_props = g.subjects(RDF.type, OWL.DatatypeProperty)
instances = g.subjects(RDF.type, OWL.NamedIndividual)

# 存储每种类型对应的项目列表
items_dict = {}

# 将所有的类、对象属性、数据属性和实例添加到字典中相应的项目列表中
for c in classes:
    name = URIRef(c).split("#")[-1]
    if "class" not in items_dict:
        items_dict["class"] = []
    items_dict["class"].append(name)
    
for op in object_props:
    name = URIRef(op).split("#")[-1]
    if "object property" not in items_dict:
        items_dict["object property"] = []
    items_dict["object property"].append(name)
    
for dp in data_props:
    name = URIRef(dp).split("#")[-1]
    if "data property" not in items_dict:
        items_dict["data property"] = []
    items_dict["data property"].append(name)
    
for i in instances:
    name = URIRef(i).split("#")[-1]
    if "instance" not in items_dict:
        items_dict["instance"] = []
    items_dict["instance"].append(name)
    
items = str(items_dict)
#print(items)

openai.api_key = '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'

temperature = 0

response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
          {"role": "user", "content": "Please act like a SPARQL Query expert. First, I will give you a list of the components in the knowledge graph you are going to query on."},
          {"role": "assistant", "content": "Sure, I can help you with that! Please provide me with the list of components in your knowledge graph so that I can assist you with your SPARQL queries."},        
          {"role": "user", "content": "Please notice that, all classes, object properties, data properties and individuals you use in the query MUST directly come from the list I provide you. If my question do not contain any of them, you SHOULD find the entities in the list that match to my question and apply them. Do you understand?"},
          {"role": "assistant", "content": "Yes, I understand. Please provide me with the list of components in your knowledge graph so that I can make sure to only use those in my queries."},
          {"role": "user", "content": "Here is the name space of my ontology:'http://www.semanticweb.org/liuzhengzuo/ontologies/2023/1/enzymeontology#'. Here is the list: "+items},
          {"role": "assistant", "content": "Thank you for providing the list of components in your knowledge graph. I will make sure to only use those components in my queries. Let me know if you have any specific question or query in mind."},
          {"role": "user", "content": "My question is:'What is the enzyme, which has a sequence reference that is Sequence39?'"},
          {"role": "assistant", "content": '''Your question matches to the class 'Enzyme', the object property 'sequenceRef' and the instance 'Sequence39'. The SPARQL Query could be: 
PREFIX : <http://www.semanticweb.org/liuzhengzuo/ontologies/2023/1/enzymeontology#>

SELECT ?enzyme
WHERE {
  ?enzyme a :Enzyme;
             :sequenceRef :Sequence39.
}'''},
          {"role": "user", "content": "My question is:'"+question+"'."}
        ]
)

answer = response['choices'][0]['message']['content']
print(answer)

# 定义正则表达式
pattern = re.compile(r"SELECT(.|\n)*")

# 在回答中查找匹配的内容
match = pattern.search(answer)

# 如果找到了匹配的内容，则输出结果
if match:
    query_str = match.group()
    #print(query_str)
else:
    print("No SPARQL query found in answer")

# create a graph object and parse the OWL file
g = Graph()
g.parse("/Users/liuzhengzuo/Desktop/Example0327.owl")

# create the SPARQL query string
query_str = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

PREFIX : <http://www.semanticweb.org/liuzhengzuo/ontologies/2023/1/enzymeontology#>
"""+"\n"+query_str

print(query_str)

# prepare the query using rdflib's prepareQuery function
query = prepareQuery(query_str)

# execute the query on the graph
results = g.query(query)

# iterate over the results and print the label of the resultSheet
for row in results:
    resultSheet_uri = row["resultSheet"]
    label_query = prepareQuery('SELECT ?label WHERE { <%s> rdfs:label ?label .}' % resultSheet_uri)
    label_results = g.query(label_query)
    for label_row in label_results:
        print(label_row["label"])

# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print("Elapsed time: {:.2f} seconds".format(elapsed_time))