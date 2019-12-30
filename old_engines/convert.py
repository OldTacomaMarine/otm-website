from bs4 import BeautifulSoup, Doctype
from itertools import izip
import os
import re
import json
import yaml
import yamlordereddictloader
import collections

original_dir = "/Users/anna/Downloads/otm_ftp_dump/www/"

def new_soup(fp):
  # Preprocess
  text = fp.read();
  # Replace malformed HTML entities
  text = re.sub(r'&Amp;|&ap;', '&amp;', text)

  return BeautifulSoup(text, "html.parser")

def pairwise(iterable):
  a = iter(iterable)
  return izip(a, a)

def nonize(h):
  for k,v in h.iteritems():
    if isinstance(v, basestring):
      h[k] = v = v.strip()

    if v is not False:
      if not v or (isinstance(v, basestring) and v.lower() == "unknown"):
        h[k] = None

# Copies data from h2 to h1 if there is no h1 value
def diff(h1, h2, k):
  if not h1[k] and h2[k]:
    h1[k] = h2[k]
  elif h1[k] != h2[k]:
    if k == "location" and h1[k].endswith(", " + h2[k]):
      return
    if k == "title" and h1[k].endswith(h2[k]):
      return
    #h1[k] = '<b style="color:red;">{}<br/>?<br/>{}</b>'.format(h1[k], h2[k])
    #print "{} {}: {} != {}".format(path, k, h1[k], h2[k])

def parse_inches(s):
  if not s:
    return None

  s = re.sub(r'-|"|\s+', ' ', s)
  s = s.replace(" 1/2", ".5")
  s = s.replace(" 1/4", ".25")
  s = s.replace(" 3/4", ".75")
  return float(s)

def parse_num(s):
  if not s:
    return None

  s = s.lower()

  if s == "one":
    return 1
  elif s == "two":
    return 2
  elif s == "three":
    return 3
  elif s == "four":
    return 4
  elif s == "five":
    return 5
  elif s == "six":
    return 6
  elif s == "seven":
    return 7
  elif s == "eight":
    return 8
  elif s == "ten":
    return 10
  elif s == "sixteen":
    return 16

  return int(s)

def validate_img_exists(category, filename):
  if not filename or filename == "../images/ina.jpg":
    return False

  path = "../images/{}/{}".format(category, os.path.basename(filename))

  return os.path.exists(path)

def convert(soup, category, path, name):
  soup.title.extract()

  content = soup.find(class_="mainContent")
  if not content:
    content = soup.find(class_="maincontent")

  title = soup.h1.get_text()
  vessel = None
  if soup.h1.i:
    vessel = soup.h1.i.get_text()
  soup.h1.extract()

  img = None
  img_big = None
  if content.a and content.a.find_next("table"):
    img_big = content.a["href"]
    if img_big.endswith("jpg"):
      img = content.a.img["src"]
      content.a.extract()
    else:
      raise ValueError("non-jpg")
  elif content.img and content.img.find_next("table"):
    img = content.img["src"]
    content.img.extract()

  if not validate_img_exists(directory, img):
    img = None
  if not validate_img_exists(directory, img_big):
    img_big = None

  model = None
  serial = None
  bore = None
  stroke = None
  cylinders = None
  hp = None
  rpm = None
  owner = None
  owner_link = None
  location = None
  map_link = None
  condition = None

  for table in content.find_all("table"):
    for label_td, value_td in pairwise(table.find_all("td")):
      nop = False
      label = label_td.get_text()
      value = value_td.get_text().strip()

      if value.lower() == "unknown":
        value = None

      if not label or not value:
        if not value:
          parent = label_td.parent
          label_td.extract()
          value_td.extract()

          if parent.name == "tr" and not parent.encode_contents().strip():
            parent.extract()

        continue;

      if re.search(r'model', label, re.I):
        model = value

      elif re.search(r'engine', label, re.I):
        serial = value

      elif re.search(r'bore.*stroke', label, re.I):
        bore, stroke = value.split("x")
        bore = parse_inches(bore)
        stroke = parse_inches(stroke)

      elif re.search(r'cylinders', label, re.I):
        cylinders = parse_num(value)

      elif re.search(r'horsepower', label, re.I):
        value = value.replace(",", "")
        if "-" not in value:
          hp = int(value)
        else:
          hp = value

      elif re.search(r'rpm', label, re.I):
        if "-" not in value:
          rpm = int(value)
        else:
          rpm = value

      elif re.search(r'owner', label, re.I):
        owner = value_td.strings.next()
        if value_td.a:
          owner_link = value_td.a["href"]

      elif re.search(r'location', label, re.I):
        location = value_td.strings.next()

        if value_td.a:
          map_link = value_td.a["href"]
          if not map_link:
            map_link = None

      elif re.search(r'condition', label, re.I):
        condition = value
      else:
        nop = True

      if not nop:
        parent = label_td.parent
        label_td.extract()
        value_td.extract()

        if parent.name == "tr" and not parent.encode_contents().strip():
          parent.extract()

    if not table.encode_contents().strip():
      table.extract()

  h2 = {}
  for h in content.find_all("h2"):
    h2[h.get_text()] = h

  external_links = []
  if "External Links" in h2:
    h = h2["External Links"]
    p = h.find_next("p")

    for a in p.find_all("a"):
      if a["href"]:
        external_links.append({
          "link": a["href"],
          "text": a.encode_contents(formatter="minimal")
        })
        a.extract()

    h.extract()
    p.extract()


  history = None
  if "Engine History" in h2:
    history = ""
    h = h2["Engine History"]

    p = h.next_sibling
    while p and p.find_previous("h2") == h:
      if p.name:
        history += p.encode(formatter="minimal")
      else:
        history += p.string
      old_p = p
      p = p.next_sibling
      old_p.extract()

    h.extract()


  #modifications = []
  #if "Engine Modifications" in h2:
  #  h = h2["Engine Modifications"]
  #  p = h.find_next("p")

  #  for li in p.find_all("li"):
  #    modifications.append(li.encode_contents(formatter="minimal").strip())

  #  h.extract()
  #  p.extract()


  #recent_news = None
  #if "Recent news" in h2:
  #  h = h2["Recent news"]
  #  p = h.find_next("p")

  #  recent_news = p.encode_contents(formatter="minimal").strip()

  #  h.extract()
  #  p.extract()

  soup.head.extract()
  soup.find(class_="branding").extract()

  if soup.find(class_="subnav"):
    soup.find(class_="subnav").extract()
  if soup.find(class_="subnavE"):
    soup.find(class_="subnavE").extract()

  for br in soup.find_all("br"):
    br.extract()
  for p in soup.find_all("p"):
    if not p.encode_contents().strip():
      p.extract()
  for item in soup.contents:
    if isinstance(item, Doctype):
      item.extract()

  if content.find("div", align="center"):
    if not content.find("div", align="center").encode_contents().strip():
      content.find("div", align="center").extract()

  if not content.encode_contents().strip():
    content.extract()
  pagebg = soup.find(class_="pageBg")
  if not pagebg.encode_contents().strip():
    pagebg.extract()
  if not soup.body.encode_contents().strip():
    soup.body.extract()

  data = collections.OrderedDict()
  data["id"] = name
  data["type"] = category
  data["title"] = title
  data["vessel"] = vessel
  data["model"] = model
  data["serial"] = serial
  data["bore"] = bore
  data["stroke"] = stroke
  data["cylinders"] = cylinders
  data["hp"] = hp
  data["rpm"] = rpm
  data["owner"] = owner
  data["owner_link"] = owner_link
  data["location"] = location
  data["map"] = map_link
  data["condition"] = condition
  data["external_links"] = external_links
  data["history"] = history
  #data["modifications"] = modifications
  #data["recent_news"] = recent_news
  data["images"] = collections.OrderedDict()
  data["images"]["big"] = img_big
  data["images"]["small"] = img

  nonize(data)

  return data


def convert_index(soup, category):
  all_data = collections.OrderedDict()
  unki = 1

  for tr in soup.find_all("tr"):
    model = tr.find("td", class_="model").get_text()
    serial = tr.find("td", class_="serial").get_text()
    title = tr.find("td", class_="engine").get_text()
    vessel = tr.find("td", class_="engine").find(class_="vessel")
    if vessel:
      vessel = vessel.get_text()
    id = tr.find("td", class_="engine").a
    if id:
      id = id["href"]
      id,_ = os.path.splitext(id)
    if not id:
      id = "unknown_{}_{}".format(category, unki)
      unki += 1
    is_display = (tr.find(class_="display-prior") != None)
    bore = tr.find("td", class_="bore").get_text()
    if bore:
      bore = float(bore)
    stroke = tr.find("td", class_="stroke").get_text()
    if stroke:
      stroke = float(stroke)
    cylinders = tr.find("td", class_="cyl").get_text()
    if cylinders:
      cylinders = int(cylinders)
    hp = tr.find("td", class_="hp").get_text()
    if hp:
      hp = int(hp.replace(",", ""))
    rpm = tr.find("td", class_="rpm").get_text()
    if rpm:
      rpm = int(rpm.replace(",", ""))
    owner = tr.find("td", class_="owner").get_text()
    origin = tr.find("td", class_="origin").get_text()
    current = tr.find("td", class_="current").get_text()
    location = tr.find("td", class_="location").get_text()
    map_link = tr.find("td", class_="location").a
    if map_link:
      map_link = map_link["href"]

    data = collections.OrderedDict()
    data["id"] = id
    data["type"] = category
    data["title"] = title
    data["vessel"] = vessel
    data["is_display"] = is_display
    data["model"] = model
    data["serial"] = serial
    data["bore"] = bore
    data["stroke"] = stroke
    data["cylinders"] = cylinders
    data["hp"] = hp
    data["rpm"] = rpm
    data["owner"] = owner
    data["location"] = location
    data["map"] = map_link
    data["origin"] = origin
    data["current"] = current

    nonize(data)

    all_data[id] = data

  return all_data



for directory in ["atlas", "enterprise", "fairbanks", "washington"]:
  input_dir = directory
  output_dir = os.path.join("output", directory)

  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  all_data = []

  # Extract data from the index for this engine category
  idx_data = None
  with open(os.path.join(input_dir, "index.html")) as fp:
    soup = new_soup(fp)
    idx_data = convert_index(soup, directory)

  # Extract data from each individual engine page for this engine category
  for filename in os.listdir(input_dir):
    name, ext = os.path.splitext(filename)

    if filename == "index.html" or ext != ".html":
      continue

    path = os.path.join(directory, filename)

    with open(path) as fp:
      soup = new_soup(fp)
      data = convert(soup, directory, path, name)
      all_data.append(data)

      idx = idx_data[name]
      diff(data, idx, "id")
      diff(data, idx, "type")
      diff(data, idx, "title")
      diff(data, idx, "vessel")
      diff(data, idx, "model")
      diff(data, idx, "serial")
      diff(data, idx, "bore")
      diff(data, idx, "stroke")
      diff(data, idx, "cylinders")
      diff(data, idx, "hp")
      diff(data, idx, "rpm")
      diff(data, idx, "owner")
      diff(data, idx, "location")
      #diff(data, idx, "map")

      if data["map"] != idx["map"]:
        data["map2"] = idx["map"]

      data["origin"] = idx["origin"]
      data["current"] = idx["current"]
      data["is_display"] = idx["is_display"]

    idx_data.pop(name, None)


  for v in idx_data.values():
    all_data.append(v)

  for data in all_data:
    vessel = data.pop("vessel", None)
    title = data.pop("title", None)

    pos = re.search(r'\(([^)]+)\)$', title)
    position = None
    if pos:
      position = pos.group(1)

    if vessel:
      if position:
        title = "{} ({})".format(vessel, position)
      else:
        title = vessel

    history = data.pop("history", None)

    data_out = collections.OrderedDict()
    data_out["id"] = data.pop("id", None)
    data_out["type"] = data.pop("type", None)
    data_out["serial"] = data.pop("serial", None)
    data_out["model"] = data.pop("model", None)
    data_out["title"] = title
    data_out["vessel"] = vessel
    data_out["position"] = position
    data_out["is_display"] = data.pop("is_display", None)
    data_out["bore"] = data.pop("bore", None)
    data_out["stroke"] = data.pop("stroke", None)
    data_out["cylinders"] = data.pop("cylinders", None)
    data_out["hp"] = data.pop("hp", None)
    data_out["rpm"] = data.pop("rpm", None)
    data_out["condition"] = data.pop("condition", None)
    data_out["current_use"] = data.pop("current", None)
    data_out["original_use"] = data.pop("origin", None)
    data_out["owner"] = data.pop("owner", None)
    data_out["owner_link"] = data.pop("owner_link", None)
    data_out["location"] = data.pop("location", None)
    data_out["map"] = data.pop("map", None)
    data_out["images"] = collections.OrderedDict()
    images = data.pop("images", {})
    img_big = images.pop("big", None)
    if img_big:
      img_big = "/images/{}/{}".format(data_out["type"], os.path.basename(img_big))
    img_small = images.pop("small", None)
    if img_small:
      img_small = "/images/{}/{}".format(data_out["type"], os.path.basename(img_small))
    data_out["images"]["big"] = img_big
    data_out["images"]["small"] = img_small
    data_out["external_links"] = data.pop("external_links", None)
    nonize(data_out)

    for k in ["id", "type", "title", "images"]:
      if not data_out[k]:
        raise ValueError("No {}: {}".format(k, str(data_out)))

    if data_out["type"] == "washington":
      if data_out["images"]["big"]:
        print os.path.basename(data_out["images"]["big"])
      if data_out["images"]["small"]:
        print os.path.basename(data_out["images"]["small"])

    with open(os.path.join(output_dir, data_out["id"] + ".html"), "w") as f:
      f.write("---\n")
      yaml.dump(data_out, f, Dumper=yamlordereddictloader.SafeDumper, default_flow_style=False, width=999999)
      f.write("---\n")
      if history:
        h_soup = BeautifulSoup(history.replace("\r", ""), "html.parser")
        f.write(str(h_soup))
        f.write("\n\n")

