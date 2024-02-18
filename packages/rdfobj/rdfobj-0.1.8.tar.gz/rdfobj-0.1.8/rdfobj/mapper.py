
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
from rdflib.namespace import RDF

from jinja2 import Environment, FileSystemLoader, BaseLoader
 
import rdfextras
from urllib.parse import urldefrag
import textwrap
import importlib
import dill
import traceback
from io import StringIO


from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
from rdflib import Namespace, Graph, URIRef,Literal
from rdflib.namespace import RDF, FOAF,XSD


from .utils import *

from .meta_model import *

###utils to mock entities
class PK():
    def __init__(self,pk,cls=None,meta_label=None):
      self.pk = pk
      self.cls=cls
      self.pop_state=None
      self.exhausted=None
      self.meta_label=meta_label

    def __str__(self):
      return "PK(pk:%s,cls:%s)" %(self.pk,self.cls )
    

    def to_json(self):
        attributes = vars(self)  
        return json.dumps(attributes, indent=2 )    
    
def define_instance_from_name(module,class_name):
   #log_info("==define_instance_from_name==%s" %(class_name))
 
   if isinstance(module,str):
      module = importlib.import_module(module)

   class_ = getattr(module, class_name)
   instance = class_()
   return instance
class ModelPopulator():
    
  def __init__(self,classDict,package):
    self.classDict=classDict
    self.rdf_type_classMap=self.define_rdf_type_classMap()
    self.package_name=package
    self.templatePath_sparql = pathlib.Path().resolve().parent.absolute() / 'script/template/sparql'
    self.model_instance_dict=dict()
     
    self.list_instance = list()
    self.KEY_ONLY=1
    self.FULL_ATTR_KEYS=2
    self.attribute_error=list()
    self.max_count=None #maximum elements in list_instance (for testing)
    self.limit=1000
    self.toolbox=ModelToolBox(self.classDict)
    self.type_schema_uri = rdflib.namespace.RDF
    constdict=constantDict()
    self.type_suffix=constdict['type_suffix']
    self.dataset_file=None # if not None, we use file based in memory store
    self.in_mem=None

  def define_module_from_name(self,module_name):
    module = importlib.import_module(module_name)
    globals()[module] = module

    return module
 
  def define_instance_from_name(self,module,class_name):
   return  define_instance_from_name( module,class_name)
 

  
  
  def instance_by_uri_sparql(self,qparam):
     return self.instance_by_uri_sparql_impl(qparam,"")
  
  def instance_by_uri_sparql_impl(self,qparam,frag,do_no_type_clause=True):
    
    tpf="?s  a    {{qparam.domain_prefix}}:{{qparam.instance_class}}."
    if do_no_type_clause:
       tpf=""

    tmpl="""
    PREFIX {{qparam.domain_prefix}}: <{{qparam.domain_namespace}}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT  * 
     WHERE
     { 
      { %s
       ?s  ?p1  ?o1 .
       %s
      FILTER (  str(?s) ="{{qparam.instance_uri}}" )
     }
    }
    ORDER BY ?s
    LIMIT 200
    """ % (tpf,frag)

    j2_env = Environment(loader=BaseLoader,trim_blocks=True).from_string(tmpl)
    return j2_env.render(qparam=qparam)
  


   

  #def all_instance_by_classname_sparql_from_file(self,qparam):
#
#    j2_env = Environment(loader=FileSystemLoader("%s" %(self.templatePath_sparql)),trim_blocks=True)
#    return j2_env.get_template('getAllInstanceByClassName.rq').render(
#        qparam=qparam
#    )

  def all_instance_by_classname_sparql(self,qparam):
    tmpl="""
    PREFIX {{qparam.domain_prefix}}: <{{qparam.domain_namespace}}>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT  ?s
    WHERE
    { 
     ?s a {{qparam.domain_prefix}}:{{qparam.instance_class}}
    }
    ORDER BY ?s
    LIMIT {{qparam.limit}}
    OFFSET {{qparam.offset}}
    """
    j2_env = Environment(loader=BaseLoader,trim_blocks=True).from_string(tmpl)
    return j2_env.render(qparam=qparam)
  
    

  def limit_and_offset(self,qparam):
    tmpl="""
    LIMIT {{qparam.limit}}
    OFFSET {{qparam.offset}}
    """
    j2_env = Environment(loader=BaseLoader,trim_blocks=True).from_string(tmpl)
    return j2_env.render(qparam=qparam)
  
  def initInMem(self,dsfile):
     rdfextras.registerplugins()
     self.in_mem=rdflib.Graph()
     self.in_mem.parse(dsfile)

  def executeQuery(self,db,dataset,query,cr=None): 
      if self.dataset_file is None:
        return self.executeQueryImpl(db,dataset,query)
      else:
        if self.in_mem is None:
          self.initInMem(self.dataset_file)
        return self.executeQueryFromFileImpl(query) 
  
  def formatBindings(self,bindings):
    #print("===formatBindings===")
    rsl=[]
    for bi in bindings :   
      d={}
      for k,v in bi.items():
         if isinstance(v,URIRef) :
           tp="uri"
         else:
           tp="literal"
         d[str(k)]={'type':tp,'value':str(v)}
      rsl.append(d)    
     
    return rsl

  def executeQueryFromFileImpl(self,query ):
      #we wrap the results 
      
      procres  = self.in_mem.query(query)
      results={"results":{}}
      results["results"]["bindings"]=self.formatBindings(procres.bindings)
      #results["results"]["vars"]=procres.vars # usefull ?
      return results

  def executeQueryImpl(self,db,dataset,query,cr=None): 
      
      url=db 
      if dataset is not None and "%s" in db:
         url=db %(dataset)

      sparql = SPARQLWrapper(url)
      sparql.setQuery(query)
      sparql.setMethod('POST')
      sparql.setReturnFormat(JSON)
      if cr is not None:
        sparql.setCredentials(cr[0], cr[1])
      results = sparql.query().convert()
      return results
  
  def instances(self):
     return self.model_instance_dict
      
  
  def init_instances(self):
      # usefull to populate entities from multiple dataset
      for instance_uri in self.model_instance_dict.keys():
        inst=self.model_instance_dict[instance_uri] 
        inst.exhausted=False
        inst.pop_state=self.KEY_ONLY
        self.model_instance_dict[instance_uri]=inst

      return self.model_instance_dict
  
  ###public 
  def executePump(self,db, dataset,inputInstDict, ml,prefix,schema_uri,type_uri=None,do_populate_asso=False,level=1):
     
     inputInD=inputInstDict
     outputInD=None
     for i in range(0,level):
         #print("@@level:%s"%(level))
         outputInD=self.executePump_impl(db, dataset,inputInD, ml,prefix,schema_uri,type_uri=None,do_populate_asso=False)
         #print("len outputInD :%s"%(len(outputInD))) 
     return outputInD

  def executePump_impl(self,db, dataset,inputInstDict, ml,prefix,schema_uri,type_uri=None,do_populate_asso=False):
     # populate the missing attributes in already selected entities (with at least pk/uri ans class)
     self.model_instance_dict=inputInstDict
     qparam=self.init_qparam(prefix,schema_uri,self.limit,0)
     module=self.define_module_from_name(self.package_name)
     if type_uri is None:
        type_uri=self.type_schema_uri
     
     ukeys=list(self.model_instance_dict.keys())
     for instance_uri in ukeys:
              inst=self.model_instance_dict[instance_uri] 
              
              if isinstance(inst,PK):
                 instn=inst.cls
                
                 inst=self.cast_instance(inst,instn,module)
                 ###meta_label tag copy
                 #print("mlab:",inst.meta_label)
                  

                 self.model_instance_dict[instance_uri]=inst
              else:
                 instn=inst.__class__.__name__      
              #print(instance_uri,"  ",instn,"  ",inst.__class__.__name__ )   
              forcegoon=False
              if forcegoon==True or inst.exhausted is None or inst.exhausted==False:
                log_info("GOON PUMP %s %s" %(inst.pk,inst.exhausted)) 
                #if instn=="UnificationXref":
                #  print(inst.to_json()) 
                if instn in   self.classDict.keys():
                   metaClass=self.classDict[instn]
                   meta_label=inst.meta_label
                   qparam["instance_uri"] =instance_uri
                   qparam["instance_class"] =metaClass.name
                   inst=self.populate_inst(db,dataset,qparam, metaClass,module,type_uri,do_populate_asso,meta_label)
                   self.model_instance_dict[inst.pk]=inst 
     return self.model_instance_dict 
  
  #public
  def executeCustomQuery(self,db,dataset,query,ml,prefix,schema_uri,do_pk_only=False, tuple_result: bool = False):
     #print("--executeCustomQuery")
     #print(">>ml:",ml)
     def fctQ(param):
       #print("--fctQ")
       q=query 
       
       if 'limit' in param.keys():
          q=q+self.limit_and_offset(param)
       return q

     self.model_instance_dict={}
     self.list_instance = []

     
     qparam=self.init_qparam(prefix,schema_uri,self.limit,0)

     if tuple_result:
        self.populate_impl(qparam,None,fctQ,db,dataset,ml,None,do_pk_only, True)
        return self.truncate_list(self.list_instance)
     
     else:
        self.populate_impl(qparam,None,fctQ,db,dataset,ml,None,do_pk_only)
        return self.truncate_dict(self.model_instance_dict)

     
  def truncate_list(self,lst):
    if  self.max_count is None:
       return lst 
    else:
       return lst[:self.max_count]
    
  def truncate_dict(self,dt):
    if  self.max_count is None:
       return dt 
    else:
       ix=0
       mapd={}
       for k in dt.keys():
          ix+=1
          if ix <=self.max_count:
            mapd[k]=dt[k]
          else:
             break

       return mapd
    
  def populate_domain_instance(self,db,dataset,prefix,schema_uri,type_uri=None,do_pk_only=False):
     
     varmeta={}
     varmeta['vartag']="s"
     varmeta=self.check_varmeta(varmeta)
     fct=self.all_instance_by_classname_sparql
     self.model_instance_dict={}
     for k in self.classDict.keys():
      
        metaClass=self.classDict[k]
        
        varmeta['class']=metaClass.name

        qparam=self.init_qparam(prefix,schema_uri,self.limit,0)
         
        if unexpected_name(metaClass.name)==False:
          qparam["instance_class"] =metaClass.name
          #print(qparam)  
          self.populate_impl(qparam,metaClass,fct,db,dataset,[varmeta],type_uri,do_pk_only)
     return self.model_instance_dict
  

  def init_qparam(self,prefix,schema_uri,limit,offset):

      qparam=dict()    
      qparam["domain_prefix"]=prefix 
      qparam["domain_namespace"]=schema_uri 
      qparam["limit"]=self.limit
      qparam["offset"]=0

      return qparam

  def check_varmeta(self,varmeta) :
     
     for k in ["label","vartag"]:
       if k not in varmeta.keys():
         varmeta[k]=None
     return varmeta
  
  def filter_binding_var_and_types(self,bindings):
       
       nb=[]
       nbt=[]
       for result in bindings:
          r={}
          rt={}
          for k in result.keys():
             if k.endswith(self.type_suffix):
                rt[k]=result[k]
             else:
                r[k]=result[k]
          nb.append(r)      
          nbt.append(rt)      

       return nb,nbt

  def populate_impl(self,qpara,metaClass,fct,db,dataset,ml ,type_uri=None, do_pk_only=False, tuple_result: bool = False):
         unknownClass=False
         if metaClass is None:
           unknownClass=True # multiple class option due to EntityNode (OR)

         do_populate_asso=True 
         qparam=copy.deepcopy(qpara)  

         if type_uri is None:
           type_uri=self.type_schema_uri

         #TODO: optimize with inst.exhausted
    
         module=self.define_module_from_name(self.package_name)
      #log_info(module)

      
         mt={}
         for varmeta in ml:
           mt[varmeta['vartag']]=varmeta
     
      ###
      #   log_info("---------mt----")
      #   for k in mt.keys():
      #     log_info("mt:k:" +str(k))
      #   log_info("---------------")         
      ###
         goon=True
         while goon==True:
           
           query=fct(qparam)

            
           log_info(query)   
           #print(query)      
           results=self.executeQuery(db,dataset,query)
           #print(results)
           bindings= results["results"]["bindings"]
           if unknownClass==True:
              # we expect %x_t_y_p_e vars
              bindings,bind_types=self.filter_binding_var_and_types(bindings)

           #log_info("========GOON %s  %s = %s  len %s" %(k,goon, qparam["offset"] ,len(bindings)) )    
           if bindings is None or len(bindings)==0:
              goon=False  
           else:
              qparam["offset"]=qparam["offset"]+qparam["limit"]
              
           #log_info(results)
           #log_info("============================================================")
           
           countel=-1
           for result in bindings:
             countel+=1
             ########warning attention : on a aussi des assos !!! ????


             
             if unknownClass==True:
                 btypes=bind_types[countel]
                 for vtag_type in btypes.keys():
                   #print("vtag_type:-%s-%s-%s-" %(vtag_type,btypes[vtag_type],type(btypes[vtag_type])))
                   uri,cls=urldefrag(URIRef( btypes[vtag_type]['value']))
                   vtag=vtag_type.replace(self.type_suffix,"")
                   metaClass=self.classDict[cls]
                   varmeta=mt[vtag]
                   varmeta['class']=metaClass.name
 
      
             if unknownClass==True or metaClass.has_unexpected_name()==False:    
              # CHANGE HERE
              result_line = []
              for vartag in result.keys():
                if vartag not in mt.keys():
                   
                   raise Exception("vartag  %s not in mt.keys()" %(vartag ))

                varmeta=mt[vartag]
                if varmeta.get('class',None) is not  None: # is a class / not an association
                      
                      # use PK()
            
                      meta_label=varmeta['label']
                      varmeta=self.check_varmeta(varmeta)
                       
                      metaClass = self.classDict[varmeta['class']]
                      # print(f"{vars(metaClass) = }")
                      qparam["instance_class"]=metaClass.name
                      ############### 
                      instance_uri=result[vartag]["value"]

                      qparam["instance_uri"]=instance_uri
                      #print("qparam:",qparam)
                     
                      if do_pk_only:
            
                        if self.model_instance_dict.get(instance_uri) is None:
                          inst=PK(instance_uri,str(metaClass.name),meta_label)
                        else:
                           inst = self.model_instance_dict.get(instance_uri)

            
                        if tuple_result:
                          result_line.append(inst)
                      else:   
                        inst=self.populate_inst(db,dataset,qparam, metaClass,module,type_uri,do_populate_asso,meta_label)

                      self.model_instance_dict[inst.pk]=inst
             if tuple_result:
              self.list_instance.append(result_line.copy())
             #for testing purpose
             if self.max_count is not None and len(self.model_instance_dict.keys() ) >= self.max_count:
                goon=False



  def populate_inst(self,db,dataset,qparam, metaClass,module,type_uri,do_populate_asso,meta_label=None):
                      
                      inst=self.inst_create_or_get(db,dataset,qparam,metaClass.name,metaClass,module,type_uri)
                      self.model_instance_dict[inst.pk]=inst
                      #print(">populate_inst %s" %(inst.pk))
                      #EntityNode>label copied in entity instance as meta_label:
                      if meta_label is not None:
                         inst.meta_label=meta_label

                      meta_att_list=self.toolbox.getMetaAttributeFromHierarchy(metaClass)
                      #print("pop1 %s" %(inst))
                      for meta_att in meta_att_list:
                          if meta_att.base==False and do_populate_asso==True:
                            attn=meta_att.name   
                            clname_att=meta_att.type 
                            try: 
                              att_getter=getattr(inst,'get_'+attn)
                              attval=att_getter()
                              if attval is not None: 
                                #print("!!attval not none")
                                att_qparam=copy.deepcopy(qparam)  
                                att_qparam["offset"]=0
                                att_qparam["limit"]=self.limit  
                                att_qparam["instance_uri"]=attval.pk
                                att_qparam["instance_class"]=clname_att  
                                matt_class=self.toolbox.getMetaClassByClassName(clname_att)
                                #print(att_qparam)
                                inst_att=self.inst_create_or_get(db,dataset,att_qparam,matt_class.name,matt_class,module,type_uri)
                                #print("  >>adding inst_att %s" %(inst_att.pk) )
                                self.model_instance_dict[inst_att.pk]=inst_att
                                att_setter=getattr(inst,'set_'+attn)
                                att_setter(inst_att)
                                #print("pop2 %s" %(inst_att))

                            except AttributeError:
                              einf=sys.exc_info()  
                              err1 = einf[0]
                              err2 = einf[1]  
                              emsg="1: %s=%s; %s ; %s ;%s  " %(inst.__class__,metaClass.name,attn,err1,err2)
                              self.attribute_error.append(emsg)
                      return inst                  
                    
  def simple_class_name(self,lcn):
   
      sp=lcn.split(".")
      cn=sp[len(sp)-1]
      return cn

  def class_name_from_instance(self,inst):
      cn = str(type(inst)).split("'")[1]
      return cn
 
  def cast_instance(self,source_inst,target_class,module):
        
    target_inst =self.define_instance_from_name(module,target_class)

    for key, value in source_inst.__dict__.items():
        target_inst.__dict__[key] = value
    return target_inst
  
  def inst_create_or_get(self,db,dataset,qparam,cm_name,cm,module,type_uri):

           instance_uri=qparam["instance_uri"] 
           
           #log_info(instance_uri)
           #print("instance_uri:%s"%(instance_uri))
           if instance_uri is None:
                log_info("warning instance_uri  is None")
                return None
            
           dokeep=False
            
           if instance_uri in self.model_instance_dict.keys(): 
              inst=self.model_instance_dict[instance_uri]    
              if inst.exhausted is not None and inst.exhausted==True: 
                dokeep=True

           if dokeep==True:     
              #print("keep")
               
              ###########cast analysis
             
              class_simple_name=self.simple_class_name_from_instance(inst)
              #log_info(">>>%s || %s" %(class_name,class_simple_name))
              if cm_name.lower() != class_simple_name.lower():
                 #log_info("==>@@@@ Is CAST possible ? %s => %s  %s" %(class_simple_name,cm_name,inst.pop_state))
                 ## 1/ we  test if inst not full populated (regarding 1 source graph)
                 ##   (if so , inst was only referenced by a main entity at this point)
                  
                 if inst.pop_state==self.KEY_ONLY  :
                    
                 ##  2/we  test if   CAST possible       
                   if self.toolbox.is_children_class_of(cm_name,class_simple_name):
                        #we cast
                        #log_info("==>@@@@YES WE CAST1 !! %s is children of  %s" %(cm_name,class_simple_name))
                        
                        targetClass=cm_name
                        #log_info(inst)
                        inst=self.cast_instance(inst,targetClass,module)
                        #self.model_instance_dict[instance_uri]=inst
                        #log_info(inst)
                    
                 ##
           else:

              #inst=self.define_instance_triple_defined_cls(db,dataset,qparam,cm,module,type_uri)
              #print("--- define_instance_user_defined_cls ---%s" %(cm_name))
               
              inst=self.define_instance_user_defined_cls(db,dataset,qparam,cm,module,type_uri,cm_name)
              
              #print(inst.to_json())
              #print(qparam)
              #log_info("===define_instance DONE")  
              #log_info(inst)  
              #log_info("=====")  
              
           return inst
  def simple_class_name_from_instance(self,inst):  
     class_name = self.class_name_from_instance(inst)
     class_simple_name=self.simple_class_name(class_name)  
     return class_simple_name
          
  def init_clsmodel_instance(self,clname):
       cls_instance=self.define_cmodel_instance(clname)
       #log_info("@@@@===>%s %s" %(clname ,cls_instance))  
       return cls_instance
  def parse_tripe_member(self,kw,res):
    obj=None
    tp=res[kw]['type']
    if 'type' in res[kw] :
      if tp=='uri':
           uri=URIRef(res[kw]['value'])
           #log_info(dir(s_uri))
           #log_info(s_uri.toPython())   
           #url, frag = urldefrag(uri)
           #log_info(url) 
           #log_info(frag)
           obj=uri
      elif tp=='literal':
           val=res[kw]['value']
           obj=val        
    return obj,tp


  def define_rdf_type_classMap(self):
       
      rdf_type_classMap=dict()
      for k in self.classDict.keys():
           metaclass=self.classDict[k]
           rdf_type_classMap[k]=metaclass.rdf_type
      return rdf_type_classMap

  



#####################################################

############################################################ 

  def define_instance_user_defined_cls(self,db,dataset,qparam,metaClass,module,type_uri,clname):
    #clname is not None
    return self.define_instance_impl(db,dataset,qparam,metaClass,module,type_uri,clname)



###FIXME : there is null instances 
  def define_instance_triple_defined_cls(self,db,dataset,qparam,metaClass,module,type_uri):
    #clname is None
    return self.define_instance_impl(db,dataset,qparam,metaClass,module,type_uri)


  def define_instance_impl(self,db,dataset,qparam,metaClass,module,type_uri,clname=None,do_create_from_clname=False):
    #do_create_from_clname force teh type of the entity
    # default is using the rdf type in the dataset
    ###TODO paging here
    #rdf_type="%s#type"%(type_uri)
    #print("--*-*-* %s" % (type(type_uri)))
    #print(type_uri)
    if isinstance(type_uri, str):
       rdf_type="%s#type"%(type_uri)
    else:
       rdf_type=type_uri['type']
 
    #RDF = rdflib.namespace.RDF
    #MODELNS=
    inst=None
    if clname is not None and do_create_from_clname:
       # we create instance from user selected class
       inst=self.define_instance_from_name(module,clname)
       # in this case we create the entity even if there is no data in triple store

    instance_uri=qparam["instance_uri"] 
    
    ##warning : for asso the type we have can be from parent so we can not add ?s  a    bi:tp. here
    query=self.instance_by_uri_sparql(qparam)
    
    iresults=self.executeQuery(db,dataset,query)
    bindings=list()
    #print("bindings")
    for res in iresults["results"]["bindings"]:
        
        s,tp_s=self.parse_tripe_member('s',res) 
        p1,tp_p1=self.parse_tripe_member('p1',res)
        o1,tp_o1=self.parse_tripe_member('o1',res)
        tpl=dict()
        tpl['s']=s
        tpl['p1']=p1
        tpl['o1']=o1
        tpl['tp_s']=tp_s
        tpl['tp_p1']=tp_p1
        tpl['tp_o1']=tp_o1

        bindings.append(tpl)
        #log_info("@@@   %s ==%s==> %s" %(s,p1,o1))
        #log_info("   @@@   %s ==%s==> %s" %(tp_s,tp_p1,tp_o1))
        
        #print(   "@@@   %s ==%s==> %s" %(tp_s,tp_p1,tp_o1))
        if inst is None and p1==rdf_type :
           
               
            #we create instance from class defined in triples  
            # in this case we create the entity only  if there is data in triple store
            url_o1, frag_o1 = urldefrag(o1)
            clname=frag_o1
        
            #  print("!!!!!!!!!!!!!!!!!!!!!!! %s  %s %s  TP: %s" %(p1,o1,rdf_type,clname))
            inst=self.define_instance_from_name(module,clname)
            #print(inst)
    if inst is None and len(bindings) >0:
         print("ERROR:instance is None from URI %s , instantiation issue caused by missing rdf type or classe name %s" %(s,clname)) 
    if inst is None and len(bindings) ==0:
         print("WARNING:we need to create the instance from scratch . URI:%s "  %(instance_uri))

    for tpl in bindings:
        s=tpl['s'] 
        p1=tpl['p1']
        o1=tpl['o1']
        pk=str(s)
        if pk == instance_uri:
           inst.__dict__['pk']=pk
           inst.pop_state=self.FULL_ATTR_KEYS
           inst.exhausted=True #
        if p1!=rdf_type :
          try:
            self.populate_attr(metaClass,module,type_uri,inst,s,p1,o1)
          except AttributeError:
            err = sys.exc_info()[0]  
            errm = sys.exc_info()[1] 
            
            emsg="2:pk:%s:s:%s;p:%so:%s  %s - %s" %(pk,s,p1,o1,err,errm)
            self.attribute_error.append(emsg)  
        
    if inst.__dict__['pk'] is None:
       inst.__dict__['pk']=instance_uri
       inst.pop_state=self.KEY_ONLY
       inst.exhausted=True # warning must remove exhausted with another dataset /connection /file

    if inst is not None and clname is not None:
       icn=type(inst).__name__
       classChecked=self.checkClassInHeritaneCoherence(icn,clname)
       #print(">>>>>>>%s %s %s" %(icn,clname,classChecked))
       if classChecked==False:
         raise("class inheritance incoherence error %s / %s" %(icn,clname)) 
         
    return inst


  def checkClassInHeritaneCoherence(self,icn,clname):
       classChecked=False
 
       if icn==clname or self.toolbox.is_children_class_of(icn,clname):   
          classChecked=True
       return  classChecked
     
  def populate_attr(self,metaClass,module,type_uri,inst,s,p1,o1):
        #print("populate_attr %s %s %s" %(clname,p1,o1))
        url_p1, frag_p1 = urldefrag(p1)
        
        #if p1 == type_uri["type"]:
        if url_p1==str(type_uri) and frag_p1=="type":
            ##
            #log_info("url_p1=type_uri +type")
            url_o1, frag_o1 = urldefrag(o1)
            s_type=frag_o1
            #if  s_type !=clname :
            # if s_type != qparam["instance_class"]:
            #    print("WARNING UNEXPECTED TYPE %s in dataset, expected:%s" %(s_type,clname))
        else:
          #url_p1, frag_p1 = urldefrag(p1)
          attn="%s" %(frag_p1)  
          ##test if attribute exists
          asatt=False
          if "_"+attn in inst.__dict__.keys() or attn in inst.__dict__.keys() :
             asatt=True
          if asatt==False:
             # we do not raise exception because some unexpected user defined triple may exist 
             return False
           
          if type(o1)==URIRef:
                att_getter=getattr(inst,'get_'+attn)

                attval=att_getter()
 
                #attribute instanciation
                #log_info("%s == %s"%(attn, metaClass))
                meta_att=self.toolbox.getMetaAttributeByAttName(metaClass,attn,dict())
                if meta_att is None:
                   log_info("WARNING %s not found in meta class hierarchy" %(attn))
                    
                clname_att=meta_att.type
                #log_info("==att to be populated=>>> %s %s" %(attn,clname_att))
                if meta_att.base==False:
                   if attval is None: 
                      inst_att=self.define_instance_from_name(module,clname_att)
                      #we create the att
                      #log_info("created") 
                      att_setter=getattr(inst,'set_'+attn)
                      att_setter(inst_att)  
                   else:
                      #log_info("reused")
                      inst_att=attval

                   #then we populate the pk attribute (uri)
                   inst_att.pk=str(o1)
                   inst_att.pop_state=self.KEY_ONLY
                else:
                   log_info("we keep None for base type")
                #log_info("%s" %( attn) )   
          else:     
            att_setter=getattr(inst,'set_'+attn)
            att_setter(o1)
          
    


# In[6]:










class StoreClient():
    
  def __init__(self,classDict):
    self.g=None
    self.namespace_manager=None
    self.toolbox=ModelToolBox(classDict)
    self.classDict=classDict 
    self.bp_template=self.define_bp_template()
    self.custom_query_list=list()


  def define_bp_template(self):

   return """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
 xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:owl="http://www.w3.org/2002/07/owl#"
  >
</rdf:RDF>
     """
 
    
  def define_namespace_manager(self,prefix,domain):
     if self.namespace_manager is None:
      g = Graph()
      g.namespace_manager.bind(prefix, URIRef(domain))
      self.namespace_manager=g.namespace_manager
    
  def delete_from_store_by_uri_id(self,sparql,uri_id,prefix,domain):
    
  

      self.define_namespace_manager(prefix,domain)
      uri_id=self.format_sparql(URIRef(uri_id),self.namespace_manager)
    
    
      query="""

PREFIX %s:   <%s>  

DELETE { ?s ?p ?o }
WHERE { 
  %s ?p ?o.  ?s ?p ?o 
};
#id as ?p

DELETE { ?s ?p ?o }
WHERE { 
 ?s ?p  %s .  ?s ?p ?o 
}

    """ %(prefix,domain,uri_id,uri_id)


      sparql.setQuery(query)
      sparql.setReturnFormat(JSON)
      log_info(query)
      res=sparql.query()
      log_info(res)

    



  def select_all_query(self,prefix,domain_schema_uri,unwanted_subject_uri,limit,offset):
    query="""

PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX %s: <%s>

SELECT ?s ?p ?o
WHERE {
  ?s ?p ?o
   FILTER(?s != <%s>)
}
LIMIT %s
OFFSET %s
    
  """ %(prefix,domain_schema_uri,unwanted_subject_uri,limit,offset)
    return query

#log_info(query)

  def defineTerm(self,el):
    #log_info(el)
    if el["type"]=='uri':
         term= URIRef(el["value"])

    elif el["type"]=='literal':
        if "datatype" in el: 
       
          term= Literal(el["value"],datatype=el["datatype"])
        else:
          term= Literal(el["value"], datatype=XSD.string)  
    #log_info("  ==> %s"% (term))
    return term
    

    
    #term=Literal
    #return term

  def file_to_graph(self,file) :
     g = Graph()
     g.parse(file, format="xml")
     self.g=g
     return g

  def string_to_graph(self,xml) :
     f=StringIO(xml)
     g = Graph()
     g.parse(f, format="xml")
     self.g=g
     return g
  
  def rdf_xml_string(self,g=None): 
      if g is None:
         g=self.g
      rdf_xml_str  = g.serialize(format='xml')
      return rdf_xml_str 
  

  def store_to_graph(self,db,prefix,domain_schema_uri,unwanted_subject_uri,limit=1000):

    self.g = Graph()
    self.g.parse(data=self.bp_template, format="xml")    
    
    offset=0
    sparql = SPARQLWrapper(db)
    go_on=True
    while go_on==True:
      query=self.select_all_query(prefix,domain_schema_uri,unwanted_subject_uri,limit,offset)
      sparql.setQuery(query)
      sparql.setReturnFormat(JSON)
      res=sparql.query()
      results = res.convert()
      bindings=results["results"]["bindings"]
      if len(bindings)==0:
         go_on=False
      else:
        offset=offset+limit
    
      for result in bindings:
        subject =self.defineTerm(result["s"])
        predicate  =self.defineTerm(result["p"])
        obj =  self.defineTerm(result["o"])
        self.g.add((subject, predicate, obj))

    return self.g


  def extends_graph(self,sparql,size,labels,limit):
   l=labels
   if size is None or size ==0:
      return  


   for s, p, o in self.g:
      #print("%s %s %s" %(s,p,o))
    q="""
prefix bp: <http://www.biopax.org/release/biopax-level3.owl#>

SELECT  * 
WHERE
 { 
  { 
    ?s  ?p  ?o .
    FILTER (  str(?s) ="%s" )
  }
}
    """ 
    qs=q %(s)
    qo=q%(o)
    extend_query_list=list()
    if size>=1:
      extend_query_list.append(qs)
    if size>=2:
      extend_query_list.append(qo)

    for query_template in extend_query_list:    
     offset=0
    
     go_on=True
     while go_on==True:
       query=query_template + " LIMIT %s OFFSET %s" %(limit,offset)
       #print("====+====")
       #print(query)
       #print("========")
       sparql.setQuery(query)
       sparql.setReturnFormat(JSON)
       res=sparql.query()
       results = res.convert()
       bindings=results["results"]["bindings"]
       if len(bindings)==0:
         go_on=False
       else:
        offset=offset+limit
       
       for result in bindings:
         subject =self.defineTerm(result[l[0]])
         predicate  =self.defineTerm(result[l[1]])
         obj =  self.defineTerm(result[l[2]])
         self.g.add((subject, predicate, obj))
         

  def store_custom_query_to_graph(self,db,ext_size=2,labels=["s","p","o"],limit=1000):

    l=labels
    self.g = Graph()
    self.g.parse(data=self.bp_template, format="xml")    
    sparql = SPARQLWrapper(db)
    for query_template in self.custom_query_list:    
     offset=0
    
     go_on=True
     while go_on==True:
       query=query_template + " LIMIT %s OFFSET %s" %(limit,offset)
       #print("====+====")
       #print(query)
       #print("========")
       sparql.setQuery(query)
       sparql.setReturnFormat(JSON)
       res=sparql.query()
       results = res.convert()
       bindings=results["results"]["bindings"]
       if len(bindings)==0:
         go_on=False
       else:
        offset=offset+limit
       #"rdftype": { "type": "uri" , "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" } ,
       for result in bindings:
         #print(result)
         subject=None
         predicate=None
         obj=None 
         if len(l)>0 and l[0] in result.keys():
           subject =self.defineTerm(result[l[0]])
         if  len(l)>1 and  l[1] in result.keys():  
           predicate  =self.defineTerm(result[l[1]])
         if  len(l)>2 and  l[2] in result.keys():
           obj =  self.defineTerm(result[l[2]])
         # add  RDF.type in some cases ??
         self.g.add((subject, predicate, obj))

    self.extends_graph(sparql,ext_size,labels, limit)
    return self.g



  def save_graph_as_rdf_xml(self,exfile, gr=None):
    log_info("exporting %s triples in file %s" %(len(self.g),exfile))
    g=None
    if gr is not None:
       g=gr
    else:
       g=self.g
    g.serialize(destination=exfile, format='xml')
    pf=pathlib.Path(exfile)  
    try:
      pf.chmod(0o0777)   
    except:
      pass

    

    

    


  def define_rdf_type_classMap(self,classDict):
 
      rdf_type_classMap=dict()
      for k in  classDict.keys():
           metaclass= classDict[k]
           rdf_type_classMap[k]=metaclass.rdf_type
      return rdf_type_classMap



  def define_literal(self,value,datatype=None):
   if value is None:
      v=None
   else:
    #v=value.encode('unicode_escape')
      v=value
    
   if datatype is not None:   
     term= Literal(v,datatype= datatype )
   else:
     term= Literal(v, datatype=XSD.string) 
   return term




  def define_triples_data(self,inst,classDict):
   #log_info(inst)
   #log_info(inst.rdf_type)
   domain=None
   prefix=None
   data=list()
   rdf_type_map=self.define_rdf_type_classMap(classDict)
   uri_id="http:/:mydomain/565675"
   ct=0 
   for  k in   classDict.keys():
    
      cls_rdf_type=rdf_type_map[k]
      ct=ct+1
   
      if cls_rdf_type==inst.rdf_type: 
         metaclass=classDict[k]
         domain=metaclass.domain   
         prefix=metaclass.prefix   
         attributes=self.toolbox.getMetaAttributeFromHierarchy(metaclass)
         #log_info("-->%s %s = %s" %(cls_rdf_type,k,metaclass))   
         s=URIRef(inst.pk)
         #p=URIRef(RDF.type) 
         p=URIRef("rdf:type")     
         o=URIRef(inst.rdf_type)
        
         #log_info("    %s %s %s" %(s,p,o))
         elt=dict()
         elt["s"]=s
         elt["p"]=p
         elt["o"]=o 
         data.append(elt)
          
         for att in attributes:
            #log_info(att.name)
            #log_info("%s %s  %s %s" %(att.base,att.name,att.type,att.xtype))
            s1=uri_id
            p1=att.name
            o1=att.xtype 
            #log_info("    %s %s %s" %(s1,p1,o1))
            
            s=URIRef(inst.pk)
            #p=metaclass.domain + att.name
            p=URIRef(metaclass.prefix+":"+att.name)
            datatype=None
            o=None
            doshow=True
            ogetter=getattr(inst,'get_'+att.name)
            #log_info("==x=>%s" %(ogetter()))
            if att.base==True:
                 
                datatype=att.type
                atvalue=ogetter()
                if atvalue is   None: 
                   doshow=False 
                o=self.define_literal(atvalue,datatype)
            else:
 
                att_inst=ogetter()
                if att_inst is not None:
                  o=URIRef(att_inst.pk)
                else:
                    doshow=False
                  
            if doshow:    
               #log_info("  ===  %s %s %s" %(s,p,o))
               el=dict()
               el["s"]=s
               el["p"]=p
               el["o"]=o 
               data.append(el)
   return data,domain,prefix

  def format_sparql(self,term,namespace_manager=None):
    #log_info(term)
    v=term
    doquote=False 
    if  isinstance(term, URIRef) :
         
        if str(term).startswith("http"):     
            if namespace_manager:
                
                v2= namespace_manager.normalizeUri(v)
         
                if v2 ==v:
                       doquote=True
                else:
                    log_info("!! %s    == %s "%(v,v2)  )
                v=v2  
    elif  isinstance(term, Literal) :  
        v="'''%s'''" %(term)
    return v

  def update_or_insert_instance(self,sparql,inst):
        uri_id=inst.pk
        triples_data,domain,prefix=self.define_triples_data(inst,self.classDict)
        self.delete_from_store_by_uri_id(sparql,uri_id,prefix,domain)
        
        return self.insert_instance_impl(sparql,inst,triples_data,domain,prefix)
        
        
  def insert_instance(self,sparql,inst):
     triples_data,domain,prefix=self.define_triples_data(inst,self.classDict)
     return self.insert_instance_impl(sparql,inst,triples_data,domain,prefix)
    
    
  def insert_instance_impl(self,sparql,inst,triples_data,domain,prefix):
    
    self.define_namespace_manager(prefix,domain)
    content=""
     
    ct=0
    for triple in triples_data:
       
       s=triple["s"]
       p=triple["p"]
       o=triple["o"]
       s=self.format_sparql(s,self.namespace_manager)
       p=self.format_sparql(p,self.namespace_manager)
       o=self.format_sparql(o,self.namespace_manager)
       ct=ct+1
       if ct==1:
          content=content+"%s %s %s;\n"  %(s,p,o)
       else:
          content=content+"     %s %s;\n"  %(p,o)
     
    query="""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
PREFIX owl:  <http://www.w3.org/2002/07/owl#> 
PREFIX %s:   <%s>  
INSERT DATA
{
 
 
%s

} 

    """ %(prefix,domain,content)
    

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    log_info(query)
    res=sparql.query()
    log_info(res)    
 

