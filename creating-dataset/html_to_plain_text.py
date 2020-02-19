import re
import os
import sys
import string
import unicodedata
from bs4 import BeautifulSoup

class ConvertHTMLToPlainText:
  def __init__(self):
    self.regex_htm = re.compile("(.*).htm")
    self.regex_numbers = re.compile("\d+")
    self.regex_special_chars = re.compile('\s+')
    self.translator = str.maketrans("","",string.punctuation)

  # Determines percentage of numerical characters
  # in a table
  def _get_digit_percentage(self, tablestring):
      if len(tablestring)>0.0:
          numbers = sum([char.isdigit() for char in tablestring])
          length = len(tablestring)
          return numbers/length
      else:
          return 1

  def _remove_numerical_tables(self, soup):
    # Evaluates numerical character % for each table
    # and removes the table if the percentage is > 15%
    [x.extract() for x in soup.find_all('table') if self._get_digit_percentage(x.get_text())>0.15]
    return soup

  def _remove_tags(self, soup):
      # Remove HTML tags with get_text
      text = soup.get_text()
      # Replace unicode characters with their "normal" representations
      text = unicodedata.normalize('NFKD', text)
      return text

  def _convert_html(self, text):
      soup = BeautifulSoup(text, "lxml")
      soup = self._remove_numerical_tables(soup)
      text = self._remove_tags(soup)
      text = re.sub(self.regex_numbers, "", text) 
      text = re.sub(self.regex_special_chars, " ", text)
      text = text.translate(self.translator)
      text = text.lower()
      return text

  def get_text_of_form(self, text):
    required_text = ""
    try:
      required_text = self._convert_html(text)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(f"  {e}, {exc_type}, {fname}, {exc_tb.tb_lineno}")
    return required_text
