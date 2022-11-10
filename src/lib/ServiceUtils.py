import dateutil.parser
import datetime
import re

class ServiceUtils:

    @staticmethod
    def ws_info_to_object(ws_info):
        # NB capturing with the same names as documented: 
        # https://github.com/kbase/workspace_deluxe/blob/0964b09a95f9c617547d40c413d57598cd12d04c/workspace.spec#L123
        [id, workspace, owner, moddate, max_objid, user_permission,
        globalread, lockstat, metadata] = ws_info

        return {'id': id,
                'name': workspace,
                'owner': owner,
                'moddate': moddate,
                'max_objid': max_objid,
                'user_permission': user_permission,
                'globalread': globalread,
                'lockstat': lockstat,
                'metadata': metadata,
                # Synthesized
                'object_count': max_objid,
                'modified_at': ServiceUtils.iso8601ToDatetime(ws_info[3]),
                'is_public': True if globalread == 'r' else False,
                'is_narratorial': True if metadata.get('narratorial') == '1' else False
        }

    @staticmethod
    def obj_info_to_object(obj_info):
        [objid, name, type, save_date, version,
        saved_by, wsid, workspace, chsum, size, metadata] = obj_info
        [type_module, type_name, type_major_version, type_minor_version] = re.split(r"-|\.", type)

        return {'objid': objid,
                'name': name,
                'type': type,
                'save_date': save_date,
                'version': version,
                'saved_by': saved_by,
                'wsid': wsid,
                'ws': workspace,
                'chsum': chsum,
                'size': size,
                'metadata': metadata,
                # Synthesized
                'ref': f'{wsid}/{objid}/{version}',
                'type_info': {
                    'module': type_module,
                    'name': type_name,
                    'version': {
                        'major': type_major_version,
                        'minor': type_minor_version
                    }
                },
                'saved_at': ServiceUtils.iso8601ToDatetime(save_date)}

    @staticmethod
    def iso8601ToMillisSinceEpoch(date):
        epoch = datetime.datetime.utcfromtimestamp(0)
        dt = dateutil.parser.parse(date)
        utc_naive = dt.replace(tzinfo=None) - dt.utcoffset()
        return int((utc_naive - epoch).total_seconds() * 1000.0)

    @staticmethod
    def iso8601ToDatetime(iso8601_string):
        return dateutil.parser.parse(iso8601_string)

    @staticmethod
    def epochMSToDatetime(epoch_ms):
        return datetime.datetime.utcfromtimestamp(epoch_ms/1000)

    @staticmethod
    def parse_app_key(key):
        parts = (list(filter(
                    lambda part: len(part) > 0,
                    key.split('/'))))
        if len(parts) == 1:
            return {
                'name': parts[0],
                'shortRef': parts[0],
                'ref': parts[0]
            }
        elif len(parts) == 3:
            return {
                'module': parts[0],
                'name': parts[1],
                'gitCommitHash': parts[2],
                'shortRef': parts[0] + '/' + parts[1],
                'ref': parts[0] + '/' + parts[1] + '/' + parts[2]
            }
        elif len(parts) == 2:
            return {
                'module': parts[0],
                'name': parts[1],
                'shortRef': parts[0] + '/' + parts[1],
                'ret': parts[0] + '/' + parts[1]
            }
        else:
            return None