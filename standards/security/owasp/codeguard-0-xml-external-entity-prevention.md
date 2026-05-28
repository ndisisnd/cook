---
description: Disable DTDs and external entities in all XML parsers to prevent XXE and Billion Laughs attacks
alwaysApply: false
---

# XML External Entity (XXE) Prevention

Safest approach: disable DTDs entirely. If DTDs are required, disable external entities and restrict entity resolution.

## NEVER
- Use `java.beans.XMLDecoder` on untrusted content — it executes arbitrary code
- Enable `XML_PARSE_NOENT` or `XML_PARSE_DTDLOAD` in libxml2
- Allow external entity resolution without a strict allowlist
- Load schemas or DTDs over unencrypted HTTP

## ALWAYS
- Disable DTD processing as the primary defense
- Set `XMLConstants.FEATURE_SECURE_PROCESSING = true` (Java)
- Set `XIncludeAware(false)` and `ExpandEntityReferences(false)` (Java)
- Update XML libraries regularly
- Test parsers with XXE payloads in safe environments
- Use static analysis to detect XXE vulnerabilities

## Parser Configuration by Platform

| Platform | Primary defense |
|----------|----------------|
| Java (DBF/SAX/DOM4J) | `disallow-doctype-decl = true` |
| Java (StAX) | `SUPPORT_DTD = false` |
| Java (TransformerFactory) | `ACCESS_EXTERNAL_DTD = ""`, `ACCESS_EXTERNAL_STYLESHEET = ""` |
| .NET 4.5.2+ | `DtdProcessing.Prohibit`, `XmlResolver = null` |
| .NET < 4.5.2 | `ProhibitDtd = true` or `XmlResolver = null` |
| C/C++ libxerces | `setDisableDefaultEntityResolution(true)` |
| PHP < 8.0 | `libxml_set_external_entity_loader(null)` |
| Python | `defusedxml` or `lxml` with `resolve_entities=False, no_network=True` |
| iOS/macOS | `NSXMLDocument` with `.nodeLoadExternalEntitiesNever` |
| ColdFusion/Lucee | `ALLOWEXTERNALENTITIES=false`, `disallowDoctypeDecl=true` |

## If DTDs Cannot Be Disabled (Java fallback)

```java
// Disable external entity features individually
String[] toDisable = {
    "http://xml.org/sax/features/external-general-entities",
    "http://xml.org/sax/features/external-parameter-entities",
    "http://apache.org/xml/features/nonvalidating/load-external-dtd"
};
// Also: setXIncludeAware(false), setExpandEntityReferences(false)
// And install a no-op EntityResolver returning new InputSource(new StringReader(""))
```

## If DTDs Absolutely Required

- Use a custom `EntityResolver` with a strict entity allowlist
- Preprocess XML to strip dangerous `DOCTYPE` declarations before parsing

## Checklist
- [ ] DTD processing disabled on all XML parsers
- [ ] No use of `XMLDecoder` on untrusted input
- [ ] `FEATURE_SECURE_PROCESSING` enabled (Java)
- [ ] defusedxml / safe parser used (Python)
- [ ] libxml2 danger flags (`NOENT`, `DTDLOAD`) absent (C/C++)
- [ ] XML libraries pinned to current version; updates tracked
- [ ] XXE payloads included in security test suite
