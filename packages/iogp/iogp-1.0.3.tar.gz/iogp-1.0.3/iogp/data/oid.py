"""
iogp.data.oid: OID (string-based) object and OID-to-name mapping (mostly Windows certificate / code signing OIDs).

Reference:
- https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc772812(v=ws.10)
- https://support.microsoft.com/en-us/help/287547/object-ids-associated-with-microsoft-cryptography
- https://www.alvestrand.no/objectid/1.2.840.113549.1.9.html
- https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-gpnap/a48b02b2-2a10-4eb0-bed4-1807a6d2f5ad
- https://docs.microsoft.com/en-us/windows/win32/api/mscat/nf-mscat-cryptcatcdfopen
- https://sourceforge.net/p/osslsigncode/osslsigncode/ci/master/tree/osslsigncode.c

Author: Vlad Topan (vtopan/gmail)
"""

OID_MAP = {
    '0.9.2342.19200300.100.1.25': 'DomainComponent',
    '1.2.840.10040.4': 'x9algorithm',
    '1.2.840.10040.4.1': 'dsa',
    '1.2.840.10040.4.3': 'dsa-with-sha1',
    '1.2.840.10045.2.1': 'ecPublicKey',
    '1.2.840.10045.3.1.7': 'prime256v1',
    '1.2.840.113549.1.1': 'PKCS#1',
    '1.2.840.113549.1.1.1': 'RSA encryption',
    '1.2.840.113549.1.1.5': 'sha1RSA',
    '1.2.840.113549.1.1.11': 'sha256RSA',
    '1.2.840.113549.1.1.12': 'sha384RSA',
    '1.2.840.113549.1.7': 'PKCS#7',
    '1.2.840.113549.1.7.1': 'data',
    '1.2.840.113549.1.7.2': 'signedData',
    '1.2.840.113549.1.8': 'PKCS#8',
    '1.2.840.113549.1.8.1': 'modules',
    '1.2.840.113549.1.8.1.1': 'pkcs-8',
    '1.2.840.113549.1.9': 'PKCS#9',
    '1.2.840.113549.1.9.1': 'eMail',
    '1.2.840.113549.1.9.2': 'unstructuredName',
    '1.2.840.113549.1.9.3': 'contentType',
    '1.2.840.113549.1.9.4': 'messageDigest',
    '1.2.840.113549.1.9.5': 'signingTime',
    '1.2.840.113549.1.9.6': 'counterSignature',
    '1.2.840.113549.1.9.7': 'challengePassword',
    '1.2.840.113549.1.9.8': 'unstructuredAddress',
    '1.2.840.113549.1.9.16': 'smime',
    '1.2.840.113549.1.9.16.1.4': 'TSTInfo',
    '1.2.840.113549.1.9.16.2.12': 'signingCertificate',
    '1.2.840.113549.1.9.16.2.47': 'signingCertificateV2',
    '1.2.840.113549.1.9.25.4': 'sequenceNumber',
    '1.3.14.3.2.26': 'sha1',
    '1.3.14.3.2.29': 'sha1WithRSAEncryption',
    '1.3.6.1.4.1.601.10.3.1': 'UnkTSAPolicy',
    '1.3.6.1.4.1.601.10.3.2': 'UnkTACPolicy',
    '1.3.6.1.4.1.601.10.4.1': 'NTPTime',
    '1.3.6.1.4.1.601.10.4.2': 'PolicyID',
    '1.3.6.1.5.5.7.1.1': 'authorityInfoAccess',
    '1.3.6.1.5.5.7.1.12': 'logotype',
    '1.3.6.1.5.5.7.3.3': 'codeSigning',
    '1.3.6.1.5.5.7.3.8': 'timeStamping',
    '1.3.6.1.5.5.7.48.2': 'caIssuers',
    '2.5.4.3': 'CommonName',
    '2.5.4.4': 'SurName',
    '2.5.4.5': 'DeviceSerialNumber',
    '2.5.4.6': 'Country',
    '2.5.4.7': 'Locality',
    '2.5.4.8': 'State',
    '2.5.4.9': 'StreetAddress',
    '2.5.4.10': 'OrganizationalUnit',
    '2.5.4.11': 'Organization',
    '2.5.4.12': 'Title',
    '2.5.4.17': 'PostalCode',
    '2.5.4.42': 'GivenName',
    '2.5.4.43': 'Initials',
    '2.5.29.1': 'obsolete-authorityKeyIdentifier',
    '2.5.29.3': 'Certificate Policies',
    '2.5.29.4': 'Primary Key Usage Restriction',
    '2.5.29.9': 'Subject Directory Attributes',
    '2.5.29.10': 'obsolete-basicConstraints',
    '2.5.29.14': 'Subject Key Identifier',
    '2.5.29.15': 'Key Usage',
    '2.5.29.16': 'Private Key Usage Period',
    '2.5.29.17': 'Subject Alternative Name',
    '2.5.29.18': 'Issuer Alternative Name',
    '2.5.29.19': 'Basic Constraints',
    '2.5.29.20': 'CRL Number',
    '2.5.29.21': 'Reason code',
    '2.5.29.23': 'Hold Instruction Code',
    '2.5.29.24': 'Invalidity Date',
    '2.5.29.27': 'Delta CRL indicator',
    '2.5.29.28': 'Issuing Distribution Point',
    '2.5.29.29': 'Certificate Issuer',
    '2.5.29.30': 'Name Constraints',
    '2.5.29.31': 'CRL Distribution Points',
    '2.5.29.32': 'Certificate Policies',
    '2.5.29.33': 'Policy Mappings',
    '2.5.29.35': 'Authority Key Identifier',
    '2.5.29.36': 'Policy Constraints',
    '2.5.29.37': 'Extended key usage',
    '2.5.29.46': 'FreshestCRL',
    '2.16.840.1.101.3.4.2.1': 'sha256',      # defined by NIST
    '2.16.840.1.113730.1.1': 'cert-type',
    # Microsoft
    '1.3.6.1.4.1.311': 'Microsoft',
    '1.3.6.1.4.1.311.2': 'Authenticode',
    '1.3.6.1.4.1.311.2.1.4': 'SPC_INDIRECT_DATA_OBJID',
    '1.3.6.1.4.1.311.2.1.11': 'SPC_STATEMENT_TYPE_OBJID',
    '1.3.6.1.4.1.311.2.1.12': 'SPC_SP_OPUS_INFO_OBJID',
    '1.3.6.1.4.1.311.2.1.15': 'SPC_PE_IMAGE_DATA_OBJID',
    '1.3.6.1.4.1.311.2.1.10': 'SPC_SP_AGENCY_INFO_OBJID',
    '1.3.6.1.4.1.311.2.1.26': 'SPC_MINIMAL_CRITERIA_OBJID',
    '1.3.6.1.4.1.311.2.1.27': 'SPC_FINANCIAL_CRITERIA_OBJID',
    '1.3.6.1.4.1.311.2.1.28': 'SPC_LINK_OBJID',
    '1.3.6.1.4.1.311.2.1.29': 'SPC_HASH_INFO_OBJID',
    '1.3.6.1.4.1.311.2.1.30': 'SPC_SIPINFO_OBJID',
    '1.3.6.1.4.1.311.2.1.14': 'SPC_CERT_EXTENSIONS_OBJID',
    '1.3.6.1.4.1.311.2.1.18': 'SPC_RAW_FILE_DATA_OBJID',
    '1.3.6.1.4.1.311.2.1.19': 'SPC_STRUCTURED_STORAGE_DATA_OBJID',
    '1.3.6.1.4.1.311.2.1.20': 'SPC_JAVA_CLASS_DATA_OBJID',
    '1.3.6.1.4.1.311.2.1.21': 'SPC_INDIVIDUAL_SP_KEY_PURPOSE_OBJID',
    '1.3.6.1.4.1.311.2.1.22': 'SPC_COMMERCIAL_SP_KEY_PURPOSE_OBJID',
    '1.3.6.1.4.1.311.2.1.25': 'SPC_CAB_DATA_OBJID',
    '1.3.6.1.4.1.311.2.1.25': 'SPC_GLUE_RDN_OBJID',
    '1.3.6.1.4.1.311.2.2': 'CTL for Software Publishers Trusted CAs',
    '1.3.6.1.4.1.311.2.2.1': 'TRUSTED_CODESIGNING_CA_LIST',
    '1.3.6.1.4.1.311.2.2.2': 'TRUSTED_CLIENT_AUTH_CA_LIST',
    '1.3.6.1.4.1.311.2.2.3': 'TRUSTED_SERVER_AUTH_CA_LIST',
    '1.3.6.1.4.1.311.2.3.1': 'SPC_PE_IMAGE_PAGE_HASHES_V1',    # SHA-1
    '1.3.6.1.4.1.311.2.3.2': 'SPC_PE_IMAGE_PAGE_HASHES_V2',    # SHA-256
    '1.3.6.1.4.1.311.2.4.1': 'SPC_NESTED_SIGNATURE_OBJID',
    '1.3.6.1.4.1.311.3': 'Time Stamping',
    '1.3.6.1.4.1.311.3.2.1': 'SPC_TIME_STAMP_REQUEST_OBJID',
    '1.3.6.1.4.1.311.3.3.1': 'RFC3161_CounterSign',
    '1.3.6.1.4.1.311.4': 'Permissions',
    '1.3.6.1.4.1.311.10': 'Crypto 2.0',
    '1.3.6.1.4.1.311.10.1': 'CTL',
    '1.3.6.1.4.1.311.10.1.1': 'SORTED_CTL',
    '1.3.6.1.4.1.311.10.2': 'NEXT_UPDATE_LOCATION',
    '1.3.6.1.4.1.311.10.3.1': 'KP_CTL_USAGE_SIGNING',
    '1.3.6.1.4.1.311.10.3.2': 'KP_TIME_STAMP_SIGNING',
    '1.3.6.1.4.1.311.10.3.3': 'SERVER_GATED_CRYPTO',
    '1.3.6.1.4.1.311.10.3.3.1': 'SERIALIZED',
    '1.3.6.1.4.1.311.10.3.4': 'EFS_CRYPTO',
    '1.3.6.1.4.1.311.10.3.4.1': 'EFS_RECOVERY',
    '1.3.6.1.4.1.311.10.3.5': 'WHQL_CRYPTO',
    '1.3.6.1.4.1.311.10.3.6': 'NT5_CRYPTO',
    '1.3.6.1.4.1.311.10.3.7': 'OEM_WHQL_CRYPTO',
    '1.3.6.1.4.1.311.10.3.8': 'EMBEDDED_NT_CRYPTO',
    '1.3.6.1.4.1.311.10.3.9': 'ROOT_LIST_SIGNER',
    '1.3.6.1.4.1.311.10.3.10': 'KP_QUALIFIED_SUBORDINATION',
    '1.3.6.1.4.1.311.10.3.11': 'KP_KEY_RECOVERY',
    '1.3.6.1.4.1.311.10.3.12': 'KP_DOCUMENT_SIGNING',
    '1.3.6.1.4.1.311.10.4.1': 'YESNO_TRUST_ATTR',
    '1.3.6.1.4.1.311.10.5.1': 'DRM',
    '1.3.6.1.4.1.311.10.5.2': 'DRM_INDIVIDUALIZATION',
    '1.3.6.1.4.1.311.10.6.1': 'LICENSES',
    '1.3.6.1.4.1.311.10.6.2': 'LICENSE_SERVER',
    '1.3.6.1.4.1.311.10.7': 'MICROSOFT_RDN_PREFIX',
    '1.3.6.1.4.1.311.10.7.1': 'KEYID_RDN',
    '1.3.6.1.4.1.311.10.8.1': 'REMOVE_CERTIFICATE',
    '1.3.6.1.4.1.311.10.9.1': 'CROSS_CERT_DIST_POINTS',
    '1.3.6.1.4.1.311.10.10': 'Microsoft CMC OIDs',
    '1.3.6.1.4.1.311.10.10.1': 'CMC_ADD_ATTRIBUTES',
    '1.3.6.1.4.1.311.10.11': 'Microsoft certificate property OIDs',
    '1.3.6.1.4.1.311.10.11.': 'CERT_PROP_ID_PREFIX',
    '1.3.6.1.4.1.311.10.12': 'CryptUI',
    '1.3.6.1.4.1.311.10.12.1': 'ANY_APPLICATION_POLICY',
    '1.3.6.1.4.1.311.12': 'Catalog',
    '1.3.6.1.4.1.311.12.1.1': 'CATALOG_LIST',
    '1.3.6.1.4.1.311.12.1.2': 'CATALOG_LIST_MEMBER',
    '1.3.6.1.4.1.311.12.1.3': 'CATALOG_LIST_MEMBER_V2',
    '1.3.6.1.4.1.311.12.2.1': 'CAT_NAMEVALUE_OBJID',
    '1.3.6.1.4.1.311.12.2.2': 'CAT_MEMBERINFO_OBJID',
    '1.3.6.1.4.1.311.12.2.3': 'CAT_MEMBERINFO2_OBJID',
    '1.3.6.1.4.1.311.13': 'Microsoft PKCS10 OIDs',
    '1.3.6.1.4.1.311.13.1': 'RENEWAL_CERTIFICATE',
    '1.3.6.1.4.1.311.13.2.1': 'ENROLLMENT_NAME_VALUE_PAIR',
    '1.3.6.1.4.1.311.13.2.2': 'ENROLLMENT_CSP_PROVIDER',
    '1.3.6.1.4.1.311.15': 'Microsoft Java',
    '1.3.6.1.4.1.311.16': 'Microsoft Outlook / Exchange',
    '1.3.6.1.4.1.311.16.4': 'Outlook Express',
    '1.3.6.1.4.1.311.17': 'Microsoft PKCS12 attributes',
    '1.3.6.1.4.1.311.17.1': 'LOCAL_MACHINE_KEYSET',
    '1.3.6.1.4.1.311.18': 'Microsoft Hydra',
    '1.3.6.1.4.1.311.19': 'Microsoft ISPU Test',
    '1.3.6.1.4.1.311.20': 'Microsoft Enrollment Infrastructure',
    '1.3.6.1.4.1.311.20.1': 'AUTO_ENROLL_CTL_USAGE',
    '1.3.6.1.4.1.311.20.2': 'ENROLL_CERTTYPE_EXTENSION',
    '1.3.6.1.4.1.311.20.2.1': 'ENROLLMENT_AGENT',
    '1.3.6.1.4.1.311.20.2.2': 'KP_SMARTCARD_LOGON',
    '1.3.6.1.4.1.311.20.2.3': 'NT_PRINCIPAL_NAME',
    '1.3.6.1.4.1.311.20.3': 'CERT_MANIFOLD',
    '1.3.6.1.4.1.311.21': 'Microsoft CertSrv Infrastructure',
    '1.3.6.1.4.1.311.21.1': 'CERTSRV_CA_VERSION',
    '1.3.6.1.4.1.311.21.2': 'CERTSRV_PREVIOUS_CERT_HASH',
    '1.3.6.1.4.1.311.21.7': 'CERTIFICATE_TEMPLATE',
    '1.3.6.1.4.1.311.21.10': 'APPLICATION_CERT_POLICIES',
    '1.3.6.1.4.1.311.25': 'Microsoft Directory Service',
    '1.3.6.1.4.1.311.25.1': 'NTDS_REPLICATION',
    '1.3.6.1.4.1.311.30': 'IIS',
    '1.3.6.1.4.1.311.31': 'Windows updates and service packs',
    '1.3.6.1.4.1.311.31.1': 'PRODUCT_UPDATE',
    '1.3.6.1.4.1.311.40': 'Fonts',
    '1.3.6.1.4.1.311.41': 'Microsoft Licensing and Registration',
    '1.3.6.1.4.1.311.42': 'Microsoft Corporate PKI (ITG)',
    '1.3.6.1.4.1.311.88': 'CAPICOM',
    '1.3.6.1.4.1.311.88': 'CAPICOM',
    '1.3.6.1.4.1.311.88.1': 'CAPICOM_VERSION',
    '1.3.6.1.4.1.311.88.2': 'CAPICOM_ATTRIBUTE',
    '1.3.6.1.4.1.311.88.2.1': 'CAPICOM_DOCUMENT_NAME',
    '1.3.6.1.4.1.311.88.2.2': 'CAPICOM_DOCUMENT_DESCRIPTION',
    '1.3.6.1.4.1.311.88.3': 'CAPICOM_ENCRYPTED_DATA',
    '1.3.6.1.4.1.311.88.3.1': 'CAPICOM_ENCRYPTED_CONTENT',
    }



class OID(str):
    """
    Class containing (a string representation of) an OID.
    """

    def __repr__(self):
        oid = super().__str__()
        return f'OID:{oid}<{OID_MAP.get(oid, "?")}>'


    @classmethod
    def extract(cls, data, offs, size):
        """
        Extract ASN.1-encoded OID (OBJECT IDENTIFIER).
        """
        oid = [data[offs] // 40, data[offs] % 40]
        if size:
            i = offs + 1
            while i < offs + size:
                val = data[i] & 0x7F
                while data[i] & 0x80 and i < offs + size:
                    i += 1
                    val = (val << 7) | (data[i] & 0x7F)
                oid.append(val)
                i += 1
        return cls('.'.join(str(e) for e in oid))
