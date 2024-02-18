#!/usr/bin/env python
 

import os

import graphviz
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import pathlib
import rdflib
import sys,time,copy,json
import pydot
from xsdata.models.enums import DataType
from xsdata.models.enums import QNames
from xsdata.formats.converter import QNameConverter
from xsdata.utils.namespaces import build_qname

from jinja2 import Environment, FileSystemLoader
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Namespace, RDF, Literal
import rdfextras
from urllib.parse import urldefrag
import textwrap
import importlib
import dill
import traceback

backup_stderr = sys.stderr
sys.stderr = open(os.devnull, "w")
from owlready2 import *
sys.stderr = backup_stderr



from .utils import *
from .meta_model import *


use_qfile=False


def extractstr(s,x,y):
    return s[x:y]

def find_indices(s, c):
    
    indices=[]
    index=-1
    for pos, char in enumerate(s):
        index+=1
        if char ==c:
            indices.append(index)

    return indices

PREFX="""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>

"""

queries_getClasses=PREFX+"""

SELECT ?class (str(?classLabel) AS ?classLabelValue) ?classMetaClass
WHERE {
  VALUES ?classMetaClass { owl:Class rdfs:Class }
  ?class rdf:type ?classMetaClass .
  ?class rdfs:label ?classLabel .
  FILTER NOT EXISTS {
    ?class owl:deprecated "true"^^xsd:boolean .
  }
}
"""


queries_getAllComments=PREFX+"""
SELECT ?s ?o
 WHERE {
 ?s ?p ?o.
      ?s   rdfs:comment ?o .
 }
ORDER BY (?s)
"""



 

queries_getClassesHierarchy=PREFX+"""SELECT ?class ?superClass
WHERE {
  VALUES ?classMetaClass1 { owl:Class rdfs:Class }
  VALUES ?classMetaClass2 { owl:Class rdfs:Class }

  ?class rdf:type ?classMetaClass1 .
  FILTER NOT EXISTS {
    ?class owl:deprecated "true"^^xsd:boolean .
  }
  ?class rdfs:subClassOf ?superClass .
  ?superClass rdf:type ?classMetaClass2 .

  FILTER NOT EXISTS {
    ?superClass owl:deprecated "true"^^xsd:boolean .
  }
}
"""


queries_getProperties=PREFX+"""
SELECT ?property (str(?propertyLabel) AS ?propertyLabelValue) ?propertyType ?propertyDomain ?propertyRange
WHERE {
  VALUES ?propertyType { owl:ObjectProperty owl:DatatypeProperty rdf:Property }

  ?property rdf:type ?propertyType .
  OPTIONAL { ?property rdfs:label ?propertyLabel . }
  FILTER NOT EXISTS {
    ?property owl:deprecated "true"^^xsd:boolean .
  }

  OPTIONAL { 
    {
    ?property (rdfs:subPropertyOf*)/rdfs:domain ?propertyDomain .
    FILTER NOT EXISTS { ?propertyDomain owl:unionOf ?domainUnionValue . }
    }
    UNION
    {
    ?property (rdfs:subPropertyOf*)/rdfs:domain/owl:unionOf ?domainUnion .
    ?domainUnion (rdf:rest*)/rdf:first ?propertyDomain .
    }
  }

  OPTIONAL { 
    {
    ?property (rdfs:subPropertyOf*)/rdfs:range ?propertyRange .
    FILTER NOT EXISTS { ?propertyRange owl:unionOf ?rangeUnionValue . }
    }
    UNION
    {
    ?property (rdfs:subPropertyOf*)/rdfs:range/owl:unionOf ?rangeUnion .
    ?rangeUnion (rdf:rest*)/rdf:first ?propertyRange .
    }
  }
}
"""


queries_getPropertyRestrictions=PREFX+"""
SELECT ?property (str(?propertyLabel) AS ?propertyLabelValue) ?restrType ?propertyDomain ?propertyRange
WHERE {
  VALUES ?restrType { owl:someValuesFrom owl:allValuesFrom }
  ?propertyDomain rdfs:subClassOf ?restr .
  ?restr rdf:type owl:Restriction .
  ?restr owl:onProperty ?property .
  ?restr ?restrType ?propertyRange .

  OPTIONAL { ?property rdfs:label ?propertyLabel . }
  FILTER NOT EXISTS {
    ?property owl:deprecated "true"^^xsd:boolean .
  }
}
"""







class ModelProcessor():
    
  def __init__(self, rdfGraphObj,scriptDir,creation_mode="lib"):
     
      self.scriptDir=scriptDir
      self.classDict=dict()
      self.pref=":"
      self.line_wrap_size=80
      self.creation_mode=creation_mode
      self.owl_file=None
      self.onto=None
      self.meta_cls_attribute_lib=dict()
      if isinstance(rdfGraphObj,Graph):
         self.rdfGraph =rdfGraphObj
      elif isinstance(rdfGraphObj,str): 
         self.owl_file=rdfGraphObj
         self.rdfGraph =self.load_graph(self.owl_file)

  def formatUriStr(self,suri):
   r=self.rdfGraph.namespace_manager.normalizeUri(suri)
   s=self.clean2p(r)
   ixl=find_indices(s,"'")
   if len(ixl)>=2:
     r=extractstr(s,ixl[0]+1,ixl[1])
   return r 
  def clean2p(self,str):
    #print(str)
    str2= str.replace(":",  self.pref)
    return str2      
  def formatstr(self,str):
    #print(str)
    str2= self.clean2p(str)
    if str2.startswith("<N"):
    #fixed blank nodes issue for dot generation
       str2=str2.replace("<","").replace(">","")
    #print(str2)   
    return str2
  
  def load_graph(self,gpath):

         rdfFormat = {}
         rdfFormat['.owl'] = 'xml'
         rdfFormat['.ttl'] = 'ttl'
         dsFormat = rdfFormat[pathlib.PurePath(gpath).suffix]
         rdfGraph = rdflib.Graph()
         #rdfGraph.load(gpath, format=dsFormat) #error caused by rdflib changed
         #fixed 
         rdfGraph.parse(gpath, format=dsFormat)
         return rdfGraph





  
    
  def defineClassHierarchy(self):
    keys=list(self.classDict.keys())
    for k in keys:
      clmodel=self.classDict[k]
      for p in clmodel.parent:
        if p in keys:
          clmodel.is_root=False 
        else:
          if p is not None:
           
            rdf_type=clmodel.prefix+":"+p 
            print("WARNING: parent class  %s not in classDict, creating it with  infered rdf_type %s" %(clmodel.parent,rdf_type))
            clmodel_root=TClassModel(p, None,self.domain,self.prefix,rdf_type)
            clmodel_root.is_root=True
         
            self.addClass(clmodel_root)
            #print(">>>>>>>><new class n0  %s" %(clmodel_root.name))
    


    keys=list(self.classDict.keys())
    for k in keys:
      clmodel=self.classDict[k]
      for p in clmodel.parent:
        if p is not None and p in keys:
          clmodel_parent=self.classDict[p]
          clmodel_parent.children.append(clmodel.name) 
          

  def displayChildren(self):

    keys=list(self.classDict.keys())
    for k in keys:
      clmodel=self.classDict[k]
      for p in clmodel.parent:
        if p is not None and p in keys:
          clmodel_parent=self.classDict[p]
          print("--%s has child %s" %(clmodel_parent.name,clmodel.name))
            
  def displayParent(self):

    keys=list(self.classDict.keys())
    for k in keys:
      clmodel=self.classDict[k]
      print("--%s has parent %s" %(clmodel.name,clmodel.parent))
            


  def createOntologySchemaGraph(self, filePath=""):
    schemaGraph = graphviz.Digraph('G')
    #schemaGraph.attr(rankdir="LR")
    schemaGraph.attr(rankdir="BT")

    prefixToNamespace = {}
    namespaceToPrefix = {}
    for currentNS in self.rdfGraph.namespace_manager.namespaces():
        prefixToNamespace[currentNS[0]] = currentNS[1]
        namespaceToPrefix[currentNS[1]] = currentNS[0]

    sparqlQuery =queries_getClasses
    if use_qfile==True:
      sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getClasses.rq').read_text()
  
    
    qres = self.rdfGraph.query(sparqlQuery)
    for row in qres:
        nodeIdent = self.formatUriStr(str(row[0]))
        nodeLabel = str(row[1])
        schemaGraph.node(nodeIdent, label=nodeLabel + "\n" + self.formatUriStr(str(row[0])), shape='box', color='black', fontcolor='black')

    sparqlQuery =queries_getClassesHierarchy
    if use_qfile==True:
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getClassesHierarchy.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    for row in qres:

        sourceIdent = self.formatstr(self.formatUriStr(str(row[0])))

        destIdent = self.formatstr(self.formatUriStr(str(row[1])))
        schemaGraph.edge(sourceIdent, destIdent, arrowhead='onormal')
    sparqlQuery =queries_getProperties
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getProperties.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    for row in qres:
        if row[3] == None or row[4] == None:
            continue
        propIdent = self.formatstr(self.formatUriStr(str(row[0])))
        propLabel = str(row[1])
        if propLabel == "":
            propLabel = self.formatUriStr(str(row[0]))
        else:
            propLabel += "\n" + self.formatUriStr(str(row[0]))
        propType = self.formatUriStr(str(row[2]))
        sourceIdent = self.formatUriStr(str(row[3]))
        destIdent = self.formatstr(self.formatUriStr(str(row[4])))
        if propType == 'owl:ObjectProperty':
            schemaGraph.edge(sourceIdent, destIdent, label=propLabel)
        elif propType == 'owl:DatatypeProperty':
            destIdent = 'str' + str(time.time())
            schemaGraph.node(destIdent, label=self.formatUriStr(str(row[4])), shape='box', color='black', fontcolor='black', style='rounded')
            schemaGraph.edge(sourceIdent, destIdent, label=propLabel)
    sparqlQuery =queries_getPropertyRestrictions
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getPropertyRestrictions.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    for row in qres:
        propIdent = self.formatstr(self.formatUriStr(str(row[0])))
        propLabel = str(row[1])
        if propLabel == "":
            propLabel = self.formatUriStr(str(row[0]))
        restrType = self.formatUriStr(str(row[2]))
        sourceIdent = self.formatstr(self.formatUriStr(str(row[3])))
        destIdent = self.formatstr(self.formatUriStr(str(row[4])))
        if restrType == 'owl:someValuesFrom':
            schemaGraph.edge(sourceIdent, destIdent, label=propLabel + " (some) ", color='grey', fontcolor='grey', arrowhead='odot')
        elif restrType == 'owl:allValuesFrom':
            schemaGraph.edge(sourceIdent, destIdent, label=propLabel + " (all) ", color='grey', fontcolor='grey', arrowhead='oinv')

    schemaGraph.save(filename=filePath)            

  def dump_meta_model(self,  fpath):  

    with open(fpath, 'wb') as f:
       m={}
       m['prefix']=self.prefix   
       m['domain']=self.domain   
       m['classDict']=self.classDict   
       dill.dump(m,f, byref=True)

  def createObjectModelGraph(self,domain=None, prefix=None):
    if self.creation_mode=='native':
         return self.createObjectModelGraphImplNative(domain, prefix)
    else:
         return self.createObjectModelGraphImplLib(domain, prefix)
        
  def createObjectModelGraphImplNative(self,domain=None, prefix=None):
    #print("start")
    self.domain=domain
    self.prefix=prefix
    comment=dict()
     

    prefixToNamespace = {}
    namespaceToPrefix = {}
    for currentNS in self.rdfGraph.namespace_manager.namespaces():
        prefixToNamespace[currentNS[0]] = currentNS[1]
        namespaceToPrefix[currentNS[1]] = currentNS[0]
    docomment=True
    if docomment==True:
      
      sparqlQuery =queries_getAllComments
      if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getAllComments.rq').read_text()
      qres = self.rdfGraph.query(sparqlQuery)
      for row in qres:
        cvalr=str(row[0])
        cval =cvalr
        suri =  str(row[1])  
        comment[suri]=cval
    sparqlQuery =queries_getClassesHierarchy
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getClassesHierarchy.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    classParent=dict() #for root class management
    #print("get_class hierarchy")
    for row in qres:
        #print(row)
        sourceuri=str(row[0])
        desturi=str(row[1])
        sourceIdent = self.formatUriStr(sourceuri)
        destIdent = self.formatUriStr(desturi)
         
        cm_name=removeFirst(sourceIdent,self.pref)
        cm_parent=removeFirst(destIdent,self.pref)
        #rdf_type=self.prefix+":"+cm_name # prefixed version
        rdf_type=sourceuri # long version
        cm=TClassModel(cm_name , cm_parent,self.domain,self.prefix,rdf_type)
        cm.pk=sourceuri
        #p_rdf_type=self.prefix+":"+cm_parent # prefixed version
        p_rdf_type=desturi # long version
        cp=TClassModel(cm_parent,None,self.domain,self.prefix,p_rdf_type)
        cp.pk=desturi
        if cp.name is not None:
           classParent[cp.name]=cp
        if cm.pk in comment.keys():
             
            self.defineComment(cm,comment[cm.pk])
        if cm.name is not None:    
        
           self.addClass(cm)
           #print(">>>>>>>><new class n2  %s" %(cm.name))

        
        
    sparqlQuery =queries_getClasses
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getClasses.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    #print("get_classes")
    for row in qres:
        #print(row)

        sourceuri=str(row[0])
        sourceliteral=str(row[1])
        sourcetypeuri=str(row[2])
        
        source = self.formatUriStr(sourceuri)
        sourcetype = self.formatUriStr(sourcetypeuri)
         
        cm_name=removeFirst(source,self.pref)
        #rdf_type=self.prefix+":"+cm_name # prefixed version
        rdf_type=sourceuri # long version
        
        cm=TClassModel(cm_name , None,self.domain,self.prefix,rdf_type)
        cm.pk=sourceuri
        if cm.pk in comment.keys():
            
            self.defineComment(cm,comment[cm.pk])
        if cm.name is not None and cm.name not in self.classDict.keys() :    
          
           self.addClass(cm)
           #print(">>>>>>>><new class n1  %s" %(cm.name))
    
 
        
        
        
    for cp_name in classParent.keys():
        if cp_name is not None and cp_name not in self.classDict.keys():
            cp=classParent[cp_name]
            if cp.pk in comment.keys():
              
              self.defineComment(cp,comment[cp.pk])
            self.addClass(cp)
            #print(">>>>>>>><new class n6  %s" %(cp.name))
            
        
    sparqlQuery =queries_getProperties
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getProperties.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    for row in qres:
        #print("===========+++++++==============")
        #print(row)
        
        if row[3] == None or row[4] == None:
            continue
        attsourceuri=str(row[0])
        propIdent = self.formatUriStr(attsourceuri)
        
        propLabel = str(row[1])
        attname=None
        
        if propLabel == "":
            propLabel = self.formatUriStr(attsourceuri)
            attname=propLabel
        else:
            propLabel += "\n" + self.formatUriStr(attsourceuri)
            attname=self.formatUriStr(attsourceuri) 
        attname=removeFirst(attname,self.pref)
        
        propType = self.formatUriStr(str(row[2]))
        
        sourceIdent = self.formatUriStr(str(row[3]))

        
        atttype = self.formatUriStr(str(row[4]))
        #print("==========")
        #print(row)
        #print(" 1 %s  :  %s %s %s" %(sourceIdent,atttype,propType,propLabel.strip()))
        if propType == 'owl:ObjectProperty':
            clsname=removeFirst(sourceIdent,self.pref)
            if clsname in self.classDict:
                cm=self.classDict[clsname]
                tp=removeFirst(atttype,self.pref)
                xtp=str(row[4])
                att=TAttributeModel(attname,False,tp,xtp)
                if attsourceuri in comment.keys():
                   
                   self.defineComment(att,comment[attsourceuri])
                cm.add_attribute(att,True)
                
            
        elif propType == 'owl:DatatypeProperty':
            #print("3 %s  :  %s" %(propType,propLabel))
              

            clsname=removeFirst(sourceIdent,self.pref)
            
            
            
            if clsname in self.classDict:
                cm=self.classDict[clsname]
                xtp=removeFirst(atttype,self.pref)
                tp=schemaType2PythonType(xtp,row[4])
                att=TAttributeModel(attname,True,tp,xtp)
                #print("___ add att %s " %(attname))
                if attsourceuri in comment.keys():
          
                   self.defineComment(att,comment[attsourceuri])

                cm.add_attribute(att,False)
            else:
                print("warning: %s not in classDict. %s" %(clsname,row ) )
  
            
            
    sparqlQuery =queries_getPropertyRestrictions
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getPropertyRestrictions.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    #print("===")
    for row in qres:
        
        propIdent = self.formatUriStr(str(row[0]))
       
        propLabel = str(row[1])
        if propLabel == "":
            propLabel = self.formatUriStr(str(row[0]))
        
        
        restrType = self.formatUriStr(str(row[2]))
        #sourceIdent = self.formatUriStr(str(row[3])).replace(":", self.pref)
        sourceIdent = self.formatUriStr(str(row[3]))
        #destIdent = self.formatUriStr(str(row[4])).replace(":", self.pref)
        destIdent = self.formatUriStr(str(row[4]))

        #print("= %s %s  %s %s " %(propLabel,restrType,sourceIdent,destIdent))

        #TODO : incluse this case
        #if restrType == 'owl:someValuesFrom':
        #    schemaGraph.edge(sourceIdent, destIdent, label=propLabel + " (some) ", color='grey', fontcolor='grey', arrowhead='odot')
        #elif restrType == 'owl:allValuesFrom':
        #    schemaGraph.edge(sourceIdent, destIdent, label=propLabel + " (all) ", color='grey', fontcolor='grey', arrowhead='oinv')

    #schemaGraph.save(filename=filePath)

    #print(" ---- convert to png with: dot -Tpng " + str(schemaPath) + " -o " + str(schemaPath)[:-3] + "png")
    #return schemaGraph,schemaPath
    return 


  def define_ontology(self):
    if self.owl_file is None:
        print("error: missing owl_file attribute is None")
        return None
    self.onto = get_ontology("file://"+self.owl_file).load()

  def describe_ontology(self):
   
   if self.onto is None:
        print("error: onto attribute  is None")
        return None
  
   cllist=list(self.onto.classes())
   for cl in cllist:
      print("==================")
      print("cl.name:%s,cl.is_a:%s" %(cl.name,cl.is_a))
      print("subclasses:%s" %(list(cl.subclasses())))
      print("ancestors:%s" %(cl.ancestors()))

   proplist=list(self.onto.object_properties())
   for prop in proplist:
      print("  obj prop:%s , domain:%s, range:%s"%(prop,prop.domain,prop.range))
    
   proplist=list(self.onto.data_properties())
   for prop in proplist:
      print("  data prop:%s  %s   , domain:%s, range:%s"%(prop._name,prop,prop.domain,prop.range))
      print("  data prop-class:%s , dir:%s"%(prop.__class__,dir(prop) ))
      for k in prop.__dict__.keys():
          print("%s=%s" %(k,prop.__dict__[k]))
#  data prop:biopax-level3.templateDirection , domain:[biopax-level3.TemplateReaction], range:[OneOf(['FORWARD', 'REVERSE'])]

  def extract_ontology_classes(self):
   
   if self.onto is None:
        print("error: onto attribute  is None")
        return None  
   proplist=list(self.onto.data_properties())
   for prop in proplist:

      name=str(prop._name)
      domain_list=prop.domain
      for domain in domain_list:
          arr=str(domain).split(".")
          cln=arr[len(arr)-1]
          #print("==%s" %(cln))
          self.meta_cls_attribute_lib[cln]=dict()

      tp=None
      xtp=None
      base=True
      att=TAttributeModel(name,base,tp,xtp)
      self.meta_cls_attribute_lib[cln][att.name]=att
      #'name', 'base', 'tp', and 'xtp'          
      range_list=prop.range
      for rang in range_list:
          #print("==>RANGX:%s" %(rang.__class__.__name__))
          if isinstance(rang,OneOf):
             enum_val=list()
             for v in rang.instances:
                 enum_val.append(str(v))
             #print("ONEOF!! %s " %(enum_val)) 
             att.enum_values=enum_val
             att.xtype="xsd:string"
             att.type="str"
          elif isinstance(rang,type):
             #print("TYPE!!")
             att.enum_values=None


#  data prop:biopax-level3.templateDirection , domain:[biopax-level3.TemplateReaction], range:[OneOf(['FORWARD', 'REVERSE'])]

  def addClass(self,cm):
     mh=0
     if cm.name in self.classDict.keys():
        fcm=self.classDict[cm.name]
        for fcmp in fcm.parent:
         for cmp in cm.parent:
           if fcmp is not None and fcmp != cmp:
            print(">>>multiple inheritance  for class %s " %(cm.name))
            if unexpected_name(cmp)==True:
               print("unexp %s" %(cmp))
            else:
              print("exp %s" %(cmp))
              fcm.parent.append(cmp)
              self.classDict[fcm.name]=fcm
              mh=1
        
     if mh==0:      
      self.classDict[cm.name]=cm

  def defineComment(self,el,com):
     el.comment=wrap(com,self.line_wrap_size)
     el.rawcomment=com

  def createObjectModelGraphImplLib(self,domain=None, prefix=None):
    #print("start")
    self.domain=domain
    self.prefix=prefix

    self.define_ontology()
    #self.describe_ontology()
    self.extract_ontology_classes()

    comment=dict()
     

    prefixToNamespace = {}
    namespaceToPrefix = {}
    for currentNS in self.rdfGraph.namespace_manager.namespaces():
        prefixToNamespace[currentNS[0]] = currentNS[1]
        namespaceToPrefix[currentNS[1]] = currentNS[0]
    docomment=True
    if docomment==True:
      # a data prop sub case
      #  data prop:biopax-level3.comment , domain:[biopax-level3.Entity | biopax-level3.UtilityClass], range:[<class 'str'>]
      sparqlQuery =queries_getAllComments
      if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getAllComments.rq').read_text()
      qres = self.rdfGraph.query(sparqlQuery)
      for crow in qres:
        csuri=str(crow[0])
        cval=str(crow[1])
        comment[csuri]=cval

        
        
    sparqlQuery =queries_getClassesHierarchy
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getClassesHierarchy.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    classParent=dict() #for root class management
    #print("get_class hierarchy")
    for row in qres:
        #print(row)
        sourceuri=str(row[0])
        desturi=str(row[1])
        #print(type(sourceuri)) 
        #print(type(desturi)) 
        #ur=URIRef(desturi)
        #print(type(ur)) 
        #print(ur.defrag()) 
        

        sourceIdent = self.formatUriStr(sourceuri)
        destIdent = self.formatUriStr(desturi)
         
        cm_name=removeFirst(sourceIdent,self.pref)
        cm_parent=removeFirst(destIdent,self.pref)
        #print("cm_parent:%s  cm_name:%s" %(cm_parent,cm_name))
        #rdf_type=self.prefix+":"+cm_name # prefixed version
        rdf_type=sourceuri # long version
        cm=TClassModel(cm_name , cm_parent,self.domain,self.prefix,rdf_type)
        cm.pk=sourceuri
        #p_rdf_type=self.prefix+":"+cm_parent # prefixed version
        p_rdf_type=desturi # long version
        cp=TClassModel(cm_parent,None,self.domain,self.prefix,p_rdf_type)
        cp.pk=desturi
        if cp.name is not None:
           classParent[cp.name]=cp
        if cm.pk in comment.keys(): 
            self.defineComment(cm,comment[cm.pk])
        if cm.name is not None:   
           #print(">>>>>>>><new class n5  %s" %(cm.name)) 
            
           self.addClass(cm)

        
        
    sparqlQuery =queries_getClasses
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getClasses.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    #print("get_classes")
    for row in qres:
        #print(row)

        sourceuri=str(row[0])
        sourceliteral=str(row[1])
        sourcetypeuri=str(row[2])
        
        source = self.formatUriStr(sourceuri)
        sourcetype = self.formatUriStr(sourcetypeuri)
          
        cm_name=removeFirst(source,self.pref)
        
        #rdf_type=self.prefix+":"+cm_name # prefixed version
        rdf_type=sourceuri # long version
        
        cm=TClassModel(cm_name , None,self.domain,self.prefix,rdf_type)
        cm.pk=sourceuri
        #print(">>>>>>>>!  %s  %s" %(cm.name,cm.pk))
        if cm.pk in comment.keys():
            
            self.defineComment(cm,comment[cm.pk])
        if cm.name is not None and cm.name not in self.classDict.keys() :    
           
           self.addClass(cm)
           #print(">>>>>>>><new class  n4 %s" %(cm.name))
    
 
        
        
        
    for cp_name in classParent.keys():
        if cp_name is not None and cp_name not in self.classDict.keys():
            cp=classParent[cp_name]
            if cp.pk in comment.keys():
              
              self.defineComment(cp,comment[cp.pk])
            self.addClass(cp)
            #print(">>>>>>>><new class n3  %s" %(cp.name))
            
        
    sparqlQuery =queries_getProperties
    if use_qfile==True: 
       sparqlQuery = pathlib.Path(self.scriptDir / 'queries/getProperties.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    for row in qres:
        #print("===========+++++++==============")
        #print(row)
        
        if row[3] == None or row[4] == None:
            continue
        attsourceuri=str(row[0])
        propIdent = self.formatUriStr(attsourceuri)
        
        propLabel = str(row[1])
        attname=None
        
        if propLabel == "":
            propLabel = self.formatUriStr(attsourceuri)
            attname=propLabel
        else:
            propLabel += "\n" + self.formatUriStr(attsourceuri)
            attname=self.formatUriStr(attsourceuri) 
        attname=removeFirst(attname,self.pref)
        
        propType = self.formatUriStr(str(row[2]))
        
        sourceIdent = self.formatUriStr(str(row[3]))

        
        atttype = self.formatUriStr(str(row[4]))
        #print("==========")
        #print(row)
        #print(" 1 %s  :  %s %s %s" %(sourceIdent,atttype,propType,propLabel.strip()))
        if propType == 'owl:ObjectProperty':
            clsname=removeFirst(sourceIdent,self.pref)
            if clsname in self.classDict:
                cm=self.classDict[clsname]
                tp=removeFirst(atttype,self.pref)
                xtp=str(row[4])
                att=TAttributeModel(attname,False,tp,xtp)
                if attsourceuri in comment.keys():
                   
                   self.defineComment(att,comment[attsourceuri])
                cm.add_attribute(att,True)
                
            
        elif propType == 'owl:DatatypeProperty':
            #print("3 %s  :  %s" %(propType,propLabel))
              

            clsname=removeFirst(sourceIdent,self.pref)
            
            
            
            if clsname in self.classDict:
                cm=self.classDict[clsname]
                xtp=removeFirst(atttype,self.pref)
                tp=schemaType2PythonType(xtp,row[4])
                att=TAttributeModel(attname,True,tp,xtp)
                #print("___ add att %s " %(attname))
                if attsourceuri in comment.keys():
                   
                   self.defineComment(att,comment[attsourceuri])
                cm.add_attribute(att,False)
            else:
                print("warning: %s not in classDict. %s" %(clsname,row ) )
  
            
            
    sparqlQuery =queries_getPropertyRestrictions
    if use_qfile==True: 
       sparqlQuery =pathlib.Path(self.scriptDir / 'queries/getPropertyRestrictions.rq').read_text()
    qres = self.rdfGraph.query(sparqlQuery)
    #print("===")
    for row in qres:
        
        propIdent = self.formatUriStr(str(row[0]))
        
        propLabel = str(row[1])
        if propLabel == "":
            propLabel = self.formatUriStr(str(row[0]))
        
        
        restrType = self.formatUriStr(str(row[2]))
        #sourceIdent = self.formatUriStr(str(row[3])).replace(":", self.pref)
        sourceIdent = self.formatUriStr(str(row[3]))
        #destIdent = self.formatUriStr(str(row[4])).replace(":", self.pref)
        destIdent = self.formatUriStr(str(row[4]))

        #print("= %s %s  %s %s " %(propLabel,restrType,sourceIdent,destIdent))

        #TODO : incluse this case
        #if restrType == 'owl:someValuesFrom':
        #    schemaGraph.edge(sourceIdent, destIdent, label=propLabel + " (some) ", color='grey', fontcolor='grey', arrowhead='odot')
        #elif restrType == 'owl:allValuesFrom':
        #    schemaGraph.edge(sourceIdent, destIdent, label=propLabel + " (all) ", color='grey', fontcolor='grey', arrowhead='oinv')

    for cln in self.meta_cls_attribute_lib.keys():
        metaclass=self.classDict[cln]
        att_dict=self.meta_cls_attribute_lib[cln]
        for att in metaclass.attribute:
            if att.name in att_dict.keys():
               attx=att_dict[att.name]
               if attx.enum_values is not None:
                 att.enum_values=attx.enum_values           
                 att.xtype=attx.xtype

    return 




