from flask_restplus import reqparse

consent_parser = reqparse.RequestParser(bundle_errors=True)
consent_parser.add_argument('timestamp', type=int, required=True, location='json',
                            help='Assigned by the client, when this consent was agreed upon')
consent_parser.add_argument('from_us', type=bool, required=True, location='json',
                            help='Is this public_key owner self-identified as a "US Person"')
consent_parser.add_argument('version', type=int, required=True, location='json',
                            help='Which version of the consent was agreed upon')
