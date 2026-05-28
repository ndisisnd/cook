---
description: XML and serialization safety — DTD/XXE hardening, schema validation, no unsafe native deserialization
alwaysApply: false
---

# XML & Serialization

## NEVER
- Allow DOCTYPE declarations or external entities in XML parsers
- Resolve network or filesystem URIs during XML parsing (XXE)
- Deserialize untrusted native objects (Java `ObjectInputStream` without allow-list, Python `pickle`, PHP `unserialize`, .NET `BinaryFormatter`)
- Use `yaml.load` (use `yaml.safe_load` only)
- Enable Jackson default typing or JSON.NET `TypeNameHandling=All`/`Auto`
- Trust XML input without strict schema validation and explicit size/depth/element limits

## ALWAYS
- Disable DTDs by default; reject DOCTYPE declarations
- Validate strictly against local, trusted XSDs
- Set explicit size, depth, and element-count limits on parsers
- Sandbox or block resolver access; no network fetches during parsing
- Monitor for unexpected DNS activity from parsing services
- For supported formats (JSON, MessagePack), validate against schema before mapping to types
- Enforce size/structure limits before parsing
- Reject polymorphic types unless strictly allow-listed
- Sign and verify serialized payloads where applicable; alert on deserialization failures

## XSLT / Transformer
- Set `ACCESS_EXTERNAL_DTD` and `ACCESS_EXTERNAL_STYLESHEET` to empty
- Disable network resource loading in stylesheets

## Hardening by language

### Java (DocumentBuilderFactory / SAXParserFactory / DOM4J)

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
```

If DTDs cannot be fully disabled, also disable: `external-general-entities`, `external-parameter-entities`, `load-external-dtd`.

### .NET

```csharp
var settings = new XmlReaderSettings {
  DtdProcessing = DtdProcessing.Prohibit,
  XmlResolver = null
};
var reader = XmlReader.Create(stream, settings);
```

### Python

```python
from defusedxml import ElementTree as ET
ET.parse('file.xml')

# or lxml
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse('filename.xml', parser)
```

## Deserialization by language
- **PHP:** prefer `json_decode`; avoid `unserialize` on untrusted input
- **Python:** never `pickle` untrusted data; use `yaml.safe_load`
- **Java:** override `ObjectInputStream#resolveClass` with an allow-list; avoid Jackson default typing; XStream allow-list
- **.NET:** avoid `BinaryFormatter`; prefer `DataContractSerializer` or `System.Text.Json`; JSON.NET `TypeNameHandling=None`

## Checklist
- [ ] DTDs off; external entities disabled in every XML parser
- [ ] Schema validation enforced; size/depth/element limits set
- [ ] No network access during parsing; resolvers restricted
- [ ] No unsafe native deserialization; allow-list when polymorphism required
- [ ] Library updates current; regression tests with XXE and deserialization payloads
