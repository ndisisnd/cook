---
description: Prevent RCE, DoS, and privilege escalation from deserializing untrusted data
alwaysApply: false
---

# Deserialization Security

## NEVER
- Deserialize untrusted data with `unserialize()` (PHP), `pickle.loads` (Python), `BinaryFormatter` (.NET), or native Java `ObjectInputStream` without class allowlisting
- Use `yaml.load()` on untrusted input — use `yaml.safe_load()`
- Enable Jackson `enableDefaultTyping()` or fastjson autotype on untrusted data
- Process XML with DTDs or external entity resolution enabled
- Trust serialized data without signature verification

## ALWAYS
- Prefer JSON/XML without type metadata over native serialization formats for untrusted input
- Validate input size, structure, and content before deserialization
- Sign serialized data and verify signatures before deserializing
- Allowlist permitted classes — Java: override `resolveClass()` to check against allowlist
- Mark sensitive Java fields `transient`
- Keep deserialization libraries updated; use XStream `allowTypes()`, not defaults
- Log deserialization attempts (size, type) and alert on failures or suspicious payloads

## Language Controls

| Language | Avoid | Use instead |
|----------|-------|-------------|
| PHP | `unserialize()` | `json_decode()` + schema validation |
| Python | `pickle.loads`, `yaml.load()` | `yaml.safe_load()`, `json.loads()` |
| Java | raw `ObjectInputStream` | allowlisted subclass; SerialKiller agent |
| .NET | `BinaryFormatter` | `DataContractSerializer`, `XmlSerializer` |
| JSON.NET | `TypeNameHandling != None` | `TypeNameHandling.None` |

## XML Hardening
```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
```
```csharp
settings.DtdProcessing = DtdProcessing.Prohibit;
```

## Checklist
- [ ] No unsafe deserializers used on untrusted input
- [ ] YAML loaded with `safe_load`; XML has DTDs/external entities disabled
- [ ] Java `resolveClass()` allowlists permitted classes
- [ ] .NET uses `DataContractSerializer` or `XmlSerializer`, not `BinaryFormatter`
- [ ] JSON.NET `TypeNameHandling` set to `None`
- [ ] Signatures verified before deserialization
- [ ] Deserialization failures logged and monitored
