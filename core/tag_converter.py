from bs4 import BeautifulSoup
from pathlib import PurePath
import sys
import re
import os
import core.exporter_thread

class TagConverter:
   #Define different type of tag behavior
   ENCLOSED_TAG = ["for", "if", "block"]
   OPEN_TAG = ["load"]
   TAG_LINK = ["script", "img", "link", "iframe"]
   
   def __init__(self, filename:str):
      self._filename = filename
      self._bs = None
      
   def convert(self, thread:core.exporter_thread.ExporterThread):
      with open(self._filename) as htmlstream:
         self._bs = BeautifulSoup(htmlstream.read().encode(), 'html.parser')
         
      self.remove_for_data()   
      
      for tag in self.ENCLOSED_TAG:
         self.extend_tag(tag, before=True, after=True)
   
      for tag in self.OPEN_TAG:
         self.extend_tag(tag, before=True)
   
      for tag in self.TAG_LINK:
         self.replace_static_links(tag)      

      content = self.replace_background_img(self.beautiful_soup.prettify())
      
         
      self._bs = None
            
      return content
      
   def convert_bss_attribute(self, attribute):
      return f"dj-{attribute}"
   
   def remove_for_data(self):
      """
      Remove extra tag used to simulate for loop content.
      """
      bss_attribute = self.convert_bss_attribute("for-data")

      for element in self.beautiful_soup.select(f'[{bss_attribute}]'):
         element.extract()   
         
   @property
   def beautiful_soup(self):
      return self._bs
   
   def extend_tag(self, django_tag, before=False, after=False):
      """
      Replace html attribute from bss to django template tag.
      Used for tag with opening and closing part : if, for, block, etc.
      """
      bss_attribute = self.convert_bss_attribute(django_tag)
      close_tag = f"{{% end{django_tag} %}}"
      
      for element in self.beautiful_soup.select(f'[{bss_attribute}]'):
         #Create content of django template tag
         #with value in html tags attributes
         attribute_value = element.attrs.pop(bss_attribute)
         open_tag = f"{{% {django_tag} {attribute_value} %}}"
   
         #Insert element in tree
         if before:
            element.insert_before(open_tag)
         if after:
            element.insert_after(close_tag)      
   
   def convert_bss_link(self, file_link):
      # TODO!!!!!!!!
      #Remove file root
      if file_link.startswith("/"):
         file_link = file_link[1:]

      path = PurePath(file_link)

      app_name = path.parts[2]
      file_type = path.parts[1]

      #Create link by switching app_name and file_type
      new_path = PurePath(app_name) / file_type / "/".join(path.parts[3:])
      return str(new_path)   
   
   def replace_static_links(self, tag_name):
      """
      Replace tag who will use django static files.

      e.g. img, script etc.
      """
      link_allowed_attributes = ["href", "src"]

      def find_ressource_attribute(element_attributes):
         """
         Find which attribute is used to point to a ressource.
         Return used attribute, and his value.
         """
         for attribute in link_allowed_attributes:
            value = element_attributes.get(attribute)
            if value:
               return attribute, value

         return None, None   
      
      static_template = '{{% static "{}" %}}'
      url_template = '{{% url "{}" %}}'
   
      for element in self.beautiful_soup.select(tag_name):
         attribute, link = find_ressource_attribute(element.attrs)
   
         if link:
            if link.startswith("http"):
               continue
            elif 'dj-to-url' in element.attrs:
               converted_link = str(link)
               element.attrs[attribute] = \
                          url_template.format(converted_link)            
            else:
               converted_link = self.convert_bss_link(link)
               element.attrs[attribute] = \
                          static_template.format(converted_link)
               
   def replace_ref(self):
      """
      Insert variable reference in specified tags.
      """
      bss_attribute = self.convert_bss_attribute("ref")
      for element in self.beautiful_soup.select(f'[{bss_attribute}]'):
         attribute_value = element.attrs.pop(bss_attribute)
         variable = f"{{{{{attribute_value}}}}}"
         element.insert(0, variable)

   def replace_background_img(self, raw_file):
      """
      Replace background-image css attribute inside
      an html file. Change it to serve file according
      to django architecture.
      """
      def url_convert(match):
         """
         Use current filename and convert it to
         a static link if needed.
         """
         url = match.group(1)
         url = url.strip('"')
         if not url.startswith("http"):
            url = self.convert_bss_link(url)
            url = f'{{% static "{url}" %}}'
         return f"url({url})"

      return re.sub("url\((.*?)\)", url_convert, raw_file)
   