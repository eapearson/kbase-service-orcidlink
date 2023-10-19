# Data

Reference data used by the service.

## Catalog

| File Name          | Source            | Comments                          |
|--------------------|-------------------|-----------------------------------|
| citation-type.json | ORCID Work Record [1] | Labels plucked from the ORCID UI! |
 | identifiers.json | ORCID External Identifiers [2] | XML document |
 | relationship-types.json | ORCID Relationship TYpes [3] | Embedded in common.xsd |
 | contributor-roles.json | Contributor Roles [4] | Note that the "old" ones are not included |



## Sources

### [1] [ORCID Citation types](https://github.com/ORCID/orcid-model/blob/e7a9c0c0060f843b2534e6100b30cab713c8aef5/src/main/resources/record_3.0/work-3.0.xsd#L254)

Manually extracted from XSD comment



### [2] [ORCID External Identifiers](https://pub.orcid.org/v2.0/identifiers)

Source is XML (appears as table in web browser).

Manually converted to json by https://jsonformatter.org/xml-to-json

### [3] [ORCID Relationship Types](https://github.com/ORCID/orcid-model/blob/e7a9c0c0060f843b2534e6100b30cab713c8aef5/src/main/resources/common_3.0/common-3.0.xsd#L1014)

Manually extracted from XSD comment

### [4] [Contributor Roles](https://github.com/ORCID/orcid-model/blob/e7a9c0c0060f843b2534e6100b30cab713c8aef5/src/main/resources/common_3.0/common-3.0.xsd#L930)

Manually extracted from XSD comment

## Notes

Most work record types simply point to the common fields; some common fields in turn point to XSD.

## See Also

### [ORCID Work Record](https://github.com/ORCID/orcid-model/blob/master/src/main/resources/record_3.0/work-3.0.xsdE)

### [ORCID Common Fields](https://github.pcom/ORCID/orcid-model/blob/master/src/main/resources/common_3.0/common-3.0.xsd)