from sqlalchemy import (
    MetaData, Table, Column, CheckConstraint, ForeignKeyConstraint, Index,
    Integer, String, Text, SMALLINT, text)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TIMESTAMP

from libweasyl.models.helpers import (
    ArrowColumn, CharSettingsColumn, JSONValuesColumn, RatingColumn, WeasylTimestampColumn, enum_column)
from libweasyl import constants


metadata = MetaData()


def default_fkey(*args, **kwargs):
    return ForeignKeyConstraint(*args, onupdate='CASCADE', ondelete='CASCADE', **kwargs)


ads = Table(
    'ads', metadata,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('owner', Text(), nullable=False),
    Column('link_target', Text(), nullable=False),
    Column('file', Integer(), nullable=False),
    Column('start', TIMESTAMP(), nullable=True),
    Column('end', TIMESTAMP(), nullable=True),
    default_fkey(['file'], ['media.mediaid'], name='ads_file_fkey'),
)

Index('ind_ads_end', ads.c.end)


api_tokens = Table(
    'api_tokens', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('token', String(length=64), primary_key=True, nullable=False),
    Column('description', String()),
    default_fkey(['userid'], ['login.userid'], name='api_tokens_userid_fkey'),
)


authbcrypt = Table(
    'authbcrypt', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('hashsum', String(length=100), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='authbcrypt_userid_fkey'),
)


blocktag = Table(
    'blocktag', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('tagid', Integer(), primary_key=True, nullable=False),
    Column('rating', RatingColumn, nullable=False),
    default_fkey(['tagid'], ['searchtag.tagid'], name='blocktag_tagid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='blocktag_userid_fkey'),
)

Index('ind_blocktag_userid', blocktag.c.userid)


charcomment = Table(
    'charcomment', metadata,
    Column('commentid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer()),
    Column('targetid', Integer()),
    Column('parentid', Integer(), nullable=False, server_default='0'),
    Column('content', Text(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('indent', Integer(), nullable=False, server_default='0'),
    Column('settings', String(length=20), nullable=False, server_default=''),
    Column('hidden_by', Integer(), nullable=True),
    default_fkey(['targetid'], ['character.charid'], name='charcomment_targetid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='charcomment_userid_fkey'),
    default_fkey(['hidden_by'], ['login.userid'], name='charcomment_hidden_by_fkey'),
)

Index('ind_charcomment_targetid', charcomment.c.targetid)


collection = Table(
    'collection', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('submitid', Integer(), primary_key=True, nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('settings', String(length=20), nullable=False, server_default='p'),
    default_fkey(['userid'], ['login.userid'], name='collection_userid_fkey'),
    default_fkey(['submitid'], ['submission.submitid'], name='collection_submitid_fkey'),
)

Index('ind_collection_userid', collection.c.userid)


comments = Table(
    'comments', metadata,
    Column('commentid', Integer(), primary_key=True),
    Column('userid', Integer(), nullable=False),
    Column('target_user', Integer(), index=True),
    Column('target_sub', Integer(), index=True),
    Column('parentid', Integer(), nullable=True),
    Column('content', Text(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('indent', Integer(), nullable=False, server_default='0'),
    Column('settings', CharSettingsColumn({
        'h': 'hidden',
        's': 'staff-note',
    }, length=20), nullable=False, server_default=''),
    Column('hidden_by', Integer(), nullable=True),
    default_fkey(['userid'], ['login.userid'], name='comments_userid_fkey'),
    default_fkey(['target_user'], ['login.userid'], name='comments_target_user_fkey'),
    default_fkey(['target_sub'], ['submission.submitid'], name='comments_target_sub_fkey'),
    default_fkey(['parentid'], ['comments.commentid'], name='comments_parentid_fkey'),
    default_fkey(['hidden_by'], ['login.userid'], name='comments_hidden_by_fkey'),
    CheckConstraint('(target_user IS NOT NULL) != (target_sub IS NOT NULL)', name='comments_target_check'),
)


commishclass = Table(
    'commishclass', metadata,
    Column('classid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('title', String(length=100), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='commishclass_userid_fkey'),
)

Index('ind_userid_title', commishclass.c.userid, commishclass.c.title, unique=True)
Index('ind_commishclass_userid', commishclass.c.userid)


commishdesc = Table(
    'commishdesc', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('content', String(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='commishdesc_userid_fkey'),
)


commishprice = Table(
    'commishprice', metadata,
    Column('priceid', Integer(), primary_key=True, nullable=False),
    Column('classid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('title', String(length=500), nullable=False),
    Column('amount_min', Integer(), nullable=False),
    Column('amount_max', Integer(), nullable=False),
    Column('settings', String(length=20), nullable=False, server_default=''),
    default_fkey(['userid'], ['login.userid'], name='commishprice_userid_fkey'),
)

Index('ind_classid_userid_title', commishprice.c.classid, commishprice.c.userid, commishprice.c.title, unique=True)


commission = Table(
    'commission', metadata,
    Column('commishid', String(), primary_key=True, nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('title', String(), nullable=False),
    Column('content', String(), nullable=False),
    Column('min_amount', Integer(), nullable=False),
    Column('max_amount', Integer()),
    Column('settings', String(), nullable=False, server_default=''),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='commission_userid_fkey'),
)


composition = Table(
    'composition', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('workid', Integer(), primary_key=True, nullable=False),
    Column('title', String(length=100), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='composition_userid_fkey'),
)


contentview = Table(
    'contentview', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('targetid', Integer(), primary_key=True, nullable=False),
    Column('type', Integer(), primary_key=True, nullable=False),
)

Index('ind_contentview_targetid', contentview.c.targetid)


cron_runs = Table(
    'cron_runs', metadata,
    Column('last_run', TIMESTAMP(), nullable=False),
)


disk_media = Table(
    'disk_media', metadata,
    Column('mediaid', Integer(), primary_key=True, nullable=False),
    Column('file_path', String(length=255), nullable=False),
    Column('file_url', String(length=255), nullable=False),
    default_fkey(['mediaid'], ['media.mediaid'], name='disk_media_mediaid_fkey'),
)


emailverify = Table(
    'emailverify', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('email', String(length=100), nullable=False, unique=True),
    default_fkey(['userid'], ['login.userid'], name='emailverify_userid_fkey'),
)


favorite = Table(
    'favorite', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('targetid', Integer(), primary_key=True, nullable=False),
    Column('type', String(length=5), primary_key=True, nullable=False, server_default=''),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('settings', String(length=20), nullable=False, server_default=''),
    default_fkey(['userid'], ['login.userid'], name='favorite_userid_fkey'),
)

Index('ind_favorite_userid', favorite.c.userid)
Index('ind_favorite_type_targetid', favorite.c.type, favorite.c.targetid, unique=False)


folder = Table(
    'folder', metadata,
    Column('folderid', Integer(), primary_key=True, nullable=False),
    Column('parentid', Integer(), nullable=False),
    Column('userid', Integer()),
    Column('title', String(length=100), nullable=False),
    Column('settings', CharSettingsColumn({
        'h': 'hidden',
        'n': 'no-notifications',
        'u': 'profile-filter',
        'm': 'index-filter',
        'f': 'featured-filter',
    }, length=20), nullable=False, server_default=''),
    default_fkey(['userid'], ['login.userid'], name='folder_userid_fkey'),
)

Index('ind_folder_userid', folder.c.userid)


forgotpassword = Table(
    'forgotpassword', metadata,
    Column('userid', Integer(), unique=True),
    Column('token', String(length=100), primary_key=True, nullable=False),
    Column('set_time', Integer(), nullable=False),
    Column('link_time', Integer(), nullable=False, server_default='0'),
    Column('address', Text(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='forgotpassword_userid_fkey'),
)


frienduser = Table(
    'frienduser', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('otherid', Integer(), primary_key=True, nullable=False),
    Column('settings', CharSettingsColumn({
        'p': 'pending',
    }, length=20), nullable=False, server_default='p'),
    Column('unixtime', WeasylTimestampColumn(), nullable=False,
           server_default=text(u"(date_part('epoch'::text, now()) - (18000)::double precision)")),
    default_fkey(['otherid'], ['login.userid'], name='frienduser_otherid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='frienduser_userid_fkey'),
)

Index('ind_frienduser_otherid', frienduser.c.otherid)
Index('ind_frienduser_userid', frienduser.c.userid)


character = Table(
    'character', metadata,
    Column('charid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer()),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('char_name', String(length=100), nullable=False, server_default=''),
    Column('age', String(length=100), nullable=False, server_default=''),
    Column('gender', String(length=100), nullable=False, server_default=''),
    Column('height', String(length=100), nullable=False, server_default=''),
    Column('weight', String(length=100), nullable=False, server_default=''),
    Column('species', String(length=100), nullable=False, server_default=''),
    Column('content', Text(), nullable=False, server_default=text(u"''::text")),
    Column('rating', RatingColumn, nullable=False),
    Column('settings', CharSettingsColumn({
        'h': 'hidden',
        'f': 'friends-only',
        't': 'tag-locked',
        'c': 'comment-locked',
    }, length=20), nullable=False, server_default=''),
    Column('page_views', Integer(), nullable=False, server_default='0'),
    default_fkey(['userid'], ['login.userid'], name='character_userid_fkey'),
)

Index('ind_character_userid', character.c.userid)


google_doc_embeds = Table(
    'google_doc_embeds', metadata,
    Column('submitid', Integer(), primary_key=True, nullable=False),
    Column('embed_url', String(length=255), nullable=False),
    default_fkey(['submitid'], ['submission.submitid'], name='google_doc_embeds_submitid_fkey'),
)


ignorecontent = Table(
    'ignorecontent', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('otherid', Integer(), primary_key=True, nullable=False),
    default_fkey(['otherid'], ['login.userid'], name='ignorecontent_otherid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='ignorecontent_userid_fkey'),
)

Index('ind_ignorecontent_userid', ignorecontent.c.userid)


ignoreuser = Table(
    'ignoreuser', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('otherid', Integer(), primary_key=True, nullable=False),
    default_fkey(['userid'], ['login.userid'], name='ignoreuser_userid_fkey'),
    default_fkey(['otherid'], ['login.userid'], name='ignoreuser_otherid_fkey'),
)

Index('ind_ignoreuser_userid', ignoreuser.c.userid)


journal = Table(
    'journal', metadata,
    Column('journalid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer()),
    Column('title', String(length=200), nullable=False),
    Column('rating', RatingColumn, nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('settings', CharSettingsColumn({
        'h': 'hidden',
        'f': 'friends-only',
        't': 'tag-locked',
        'c': 'comment-locked',
    }, length=20), nullable=False, server_default=''),
    Column('page_views', Integer(), nullable=False, server_default='0'),
    default_fkey(['userid'], ['login.userid'], name='journal_userid_fkey'),
)

Index('ind_journal_userid', journal.c.userid)


journalcomment = Table(
    'journalcomment', metadata,
    Column('commentid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer()),
    Column('targetid', Integer()),
    Column('parentid', Integer(), nullable=False, server_default='0'),
    Column('content', Text(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('indent', Integer(), nullable=False, server_default='0'),
    Column('settings', String(length=20), nullable=False, server_default=''),
    Column('hidden_by', Integer(), nullable=True),
    default_fkey(['targetid'], ['journal.journalid'], name='journalcomment_targetid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='journalcomment_userid_fkey'),
    default_fkey(['hidden_by'], ['login.userid'], name='journalcomment_hidden_by_fkey'),
)

Index('ind_journalcomment_settings', journalcomment.c.settings)
Index('ind_journalcomment_targetid_settings', journalcomment.c.targetid, journalcomment.c.settings)
Index('ind_journalcomment_targetid', journalcomment.c.targetid)


login = Table(
    'login', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('login_name', String(length=40), nullable=False, unique=True),
    Column('last_login', WeasylTimestampColumn(), nullable=False),
    Column('settings', CharSettingsColumn({
        'd': 'premium',
        'p': 'reset-password',
        'i': 'reset-birthday',
        'e': 'reset-email',
    }, {
        'account-state': {
            'b': 'banned',
            's': 'suspended',
        },
    }, length=20), nullable=False, server_default=''),
    Column('email', String(length=100), nullable=False, server_default=''),
)

Index('ind_login_login_name', login.c.login_name)


loginaddress = Table(
    'loginaddress', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('address', String(length=40), primary_key=True, nullable=False),
    default_fkey(['userid'], ['login.userid'], name='loginaddress_userid_fkey'),
)


logincreate = Table(
    'logincreate', metadata,
    Column('token', String(length=100), primary_key=True, nullable=False),
    Column('username', String(length=40), nullable=False),
    Column('login_name', String(length=40), nullable=False, unique=True),
    Column('hashpass', String(length=100), nullable=False),
    Column('email', String(length=100), nullable=False, unique=True),
    Column('birthday', WeasylTimestampColumn(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
)


logininvite = Table(
    'logininvite', metadata,
    Column('email', String(length=200), primary_key=True, nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('settings', String(length=20), nullable=False, server_default=''),
)


media = Table(
    'media', metadata,
    Column('mediaid', Integer(), primary_key=True, nullable=False),
    Column('media_type', String(length=32), nullable=False),
    Column('file_type', String(length=8), nullable=False),
    Column('attributes', JSONValuesColumn(), nullable=False, server_default=text(u"''::hstore")),
    Column('sha256', String(length=64)),
)


media_media_links = Table(
    'media_media_links', metadata,
    Column('linkid', Integer(), primary_key=True, nullable=False),
    Column('described_with_id', Integer(), nullable=False),
    Column('describee_id', Integer(), nullable=False),
    Column('link_type', String(length=32), nullable=False),
    Column('attributes', JSONValuesColumn(), nullable=False, server_default=text(u"''::hstore")),
    default_fkey(['describee_id'], ['media.mediaid'], name='media_media_links_describee_id_fkey'),
    default_fkey(['described_with_id'], ['media.mediaid'], name='media_media_links_described_with_id_fkey'),
)

Index('ind_media_media_links_describee_id', media_media_links.c.describee_id)
Index('ind_media_media_links_submitid', media_media_links.c.describee_id)
Index('ind_media_media_links_described_with_id', media_media_links.c.described_with_id, unique=False)


message = Table(
    'message', metadata,
    Column('noteid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer()),
    Column('otherid', Integer()),
    Column('user_folder', Integer(), nullable=False, server_default='0'),
    Column('other_folder', Integer(), nullable=False, server_default='0'),
    Column('title', String(length=100), nullable=False),
    Column('content', Text(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('settings', String(length=20), nullable=False, server_default='u'),
    default_fkey(['otherid'], ['login.userid'], name='message_otherid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='message_userid_fkey'),
)

Index('ind_message_otherid', message.c.otherid)
Index('ind_message_userid', message.c.userid)


oauth_bearer_tokens = Table(
    'oauth_bearer_tokens', metadata,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('clientid', String(length=32), nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('scopes', ARRAY(Text()), nullable=False),
    Column('access_token', String(length=64), nullable=False, unique=True),
    Column('refresh_token', String(length=64), nullable=False, unique=True),
    Column('expires_at', ArrowColumn(), nullable=False),
    default_fkey(['clientid'], ['oauth_consumers.clientid'], name='oauth_bearer_tokens_clientid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='oauth_bearer_tokens_userid_fkey'),
)


oauth_consumers = Table(
    'oauth_consumers', metadata,
    Column('clientid', String(length=32), primary_key=True, nullable=False),
    Column('description', Text(), nullable=False),
    Column('ownerid', Integer(), nullable=False),
    Column('grant_type', String(length=32), nullable=False),
    Column('response_type', String(length=32), nullable=False),
    Column('scopes', ARRAY(Text()), nullable=False),
    Column('redirect_uris', ARRAY(Text()), nullable=False),
    Column('client_secret', String(length=64), nullable=False),
    default_fkey(['ownerid'], ['login.userid'], name='oauth_consumers_owner_fkey'),
)


permaban = Table(
    'permaban', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('reason', Text(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='permaban_userid_fkey'),
)


premiumpurchase = Table(
    'premiumpurchase', metadata,
    Column('token', String(), primary_key=True, nullable=False),
    Column('email', String(), nullable=False),
    Column('terms', SMALLINT(), nullable=False),
)


profile = Table(
    'profile', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('username', String(length=40), nullable=False, unique=True),
    Column('full_name', String(length=100), nullable=False),
    Column('catchphrase', String(length=200), nullable=False, server_default=''),
    Column('artist_type', String(length=100), nullable=False, server_default=''),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('profile_text', Text(), nullable=False, server_default=''),
    Column('settings', String(length=20), nullable=False, server_default='ccci'),
    Column('stream_url', String(length=500), nullable=False, server_default=''),
    Column('page_views', Integer(), nullable=False, server_default='0'),
    Column('config', CharSettingsColumn({
        'b': 'show-birthday',
        '2': '12-hour-time',

        'l': 'use-only-tag-blacklist',

        'g': 'tagging-disabled',
        'd': 'premium',

        'u': 'hide-favorites-bar',
        'v': 'hide-favorites',
        'w': 'staff-shouts-only',
        'x': 'friend-shouts-only',
        'y': 'staff-notes-only',
        'z': 'friend-notes-only',
        'h': 'hide-profile-from-guests',
        'i': 'hide-profile-stats',
        'k': 'disallow-others-tag-removal',
        'r': 'disallow-others-tag-editing',

        's': 'watch-user-submissions',
        'c': 'watch-user-collections',
        'f': 'watch-user-characters',
        't': 'watch-user-stream-status',
        'j': 'watch-user-journals',
    }, {
        'tagging-level': {
            'm': 'max-rating-moderate',
            'a': 'max-rating-mature',
            'p': 'max-rating-explicit',
        },
        'thumbnail-bar': {
            'O': 'collections',
            'A': 'characters',
        },
    }, length=50), nullable=False, server_default=''),
    Column('jsonb_settings', JSONB()),
    Column('stream_time', Integer()),
    Column('stream_text', String()),
    default_fkey(['userid'], ['login.userid'], name='profile_userid_fkey'),
)


report = Table(
    'report', metadata,
    Column('target_user', Integer(), nullable=True),
    Column('target_sub', Integer(), nullable=True),
    Column('target_char', Integer(), nullable=True),
    Column('target_journal', Integer(), nullable=True),
    Column('target_comment', Integer(), nullable=True),
    Column('opened_at', ArrowColumn(), nullable=False),
    Column('urgency', Integer(), nullable=False),
    Column('closerid', Integer(), nullable=True),
    Column('settings', CharSettingsColumn({
        'r': 'under-review',
    }, length=20), nullable=False, server_default=''),
    Column('reportid', Integer(), primary_key=True, nullable=False),
    Column('closed_at', ArrowColumn(), nullable=True),
    Column('closure_reason',
           enum_column(constants.ReportClosureReason,
                       name='report_closure_reason',
                       metadata=metadata),
           nullable=True),
    Column('closure_explanation', Text(), nullable=True),
    default_fkey(['target_user'], ['login.userid'], name='report_target_user_fkey'),
    default_fkey(['target_sub'], ['submission.submitid'], name='report_target_sub_fkey'),
    default_fkey(['target_char'], ['character.charid'], name='report_target_char_fkey'),
    default_fkey(['target_journal'], ['journal.journalid'], name='report_target_journal_fkey'),
    default_fkey(['target_comment'], ['comments.commentid'], name='report_target_comment_fkey'),
    default_fkey(['closerid'], ['login.userid'], name='report_closerid_fkey'),
    CheckConstraint(
        '((target_user IS NOT NULL)::int + (target_sub IS NOT NULL)::int '
        '  + (target_char IS NOT NULL)::int + (target_journal IS NOT NULL)::int '
        '  + (target_comment IS NOT NULL)::int) = 1',
        name='report_target_check'),
    CheckConstraint(
        '((closed_at IS NOT NULL)::int + (closure_reason IS NOT NULL)::int '
        '  + (closure_explanation IS NOT NULL)::int) IN (0, 3)',
        name='report_closure_check'),
)


reportcomment = Table(
    'reportcomment', metadata,
    Column('violation', Integer(), nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('content', String(length=2000), nullable=False, server_default=''),
    Column('commentid', Integer(), primary_key=True, nullable=False),
    Column('reportid', Integer(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='reportcomment_userid_fkey'),
    default_fkey(['reportid'], ['report.reportid'], name='reportcomment_reportid_fkey'),
)


searchmapchar = Table(
    'searchmapchar', metadata,
    Column('tagid', Integer(), primary_key=True, nullable=False),
    Column('targetid', Integer(), primary_key=True, nullable=False),
    Column('settings', String(), nullable=False, server_default=''),
    default_fkey(['targetid'], ['character.charid'], name='searchmapchar_targetid_fkey'),
    default_fkey(['tagid'], ['searchtag.tagid'], name='searchmapchar_tagid_fkey'),
)

Index('ind_searchmapchar_tagid', searchmapchar.c.tagid)
Index('ind_searchmapchar_targetid', searchmapchar.c.targetid)


searchmapjournal = Table(
    'searchmapjournal', metadata,
    Column('tagid', Integer(), primary_key=True, nullable=False),
    Column('targetid', Integer(), primary_key=True, nullable=False),
    Column('settings', String(), nullable=False, server_default=''),
    default_fkey(['targetid'], ['journal.journalid'], name='searchmapjournal_targetid_fkey'),
    default_fkey(['tagid'], ['searchtag.tagid'], name='searchmapjournal_tagid_fkey'),
)

Index('ind_searchmapjournal_targetid', searchmapjournal.c.targetid)
Index('ind_searchmapjournal_tagid', searchmapjournal.c.tagid)


searchmapsubmit = Table(
    'searchmapsubmit', metadata,
    Column('tagid', Integer(), primary_key=True, nullable=False),
    Column('targetid', Integer(), primary_key=True, nullable=False),
    Column('settings', CharSettingsColumn({
        'a': 'artist-tag',
    }), nullable=False, server_default=''),
    default_fkey(['targetid'], ['submission.submitid'], name='searchmapsubmit_targetid_fkey'),
    default_fkey(['tagid'], ['searchtag.tagid'], name='searchmapsubmit_tagid_fkey'),
)

Index('ind_searchmapsubmit_tagid', searchmapsubmit.c.tagid)
Index('ind_searchmapsubmit_targetid', searchmapsubmit.c.targetid)


searchtag = Table(
    'searchtag', metadata,
    Column('tagid', Integer(), primary_key=True, nullable=False),
    Column('title', Text(), nullable=False, unique=True),
)

Index('ind_searchtag_tagid', searchtag.c.tagid)


sessions = Table(
    'sessions', metadata,
    Column('sessionid', String(length=64), primary_key=True, nullable=False),
    Column('created_at', ArrowColumn(), nullable=False, server_default=text('now()')),
    Column('userid', Integer()),
    Column('csrf_token', String(length=64)),
    Column('additional_data', JSONValuesColumn(), nullable=False, server_default=text(u"''::hstore")),
    default_fkey(['userid'], ['login.userid'], name='sessions_userid_fkey'),
)

Index('ind_sessions_created_at', sessions.c.created_at)


siteupdate = Table(
    'siteupdate', metadata,
    Column('updateid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer()),
    Column('title', String(length=100), nullable=False),
    Column('content', Text(), nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='siteupdate_userid_fkey'),
)


submission = Table(
    'submission', metadata,
    Column('submitid', Integer(), primary_key=True, nullable=False),
    Column('folderid', Integer(), nullable=True),
    Column('userid', Integer()),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('title', String(length=200), nullable=False),
    Column('content', Text(), nullable=False),
    Column('subtype', Integer(), nullable=False),
    Column('rating', RatingColumn, nullable=False),
    Column('settings', CharSettingsColumn({
        'h': 'hidden',
        'f': 'friends-only',
        'q': 'critique',
        'p': 'pool',
        'o': 'collaboration',
        't': 'tag-locked',
        'c': 'comment-locked',
        'a': 'admin-locked',
        'e': 'encored',
        'u': 'thumbnail-required',
    }, {
        'embed-type': {
            'D': 'google-drive',
            'v': 'other',
        },
    }), nullable=False, server_default=''),
    Column('page_views', Integer(), nullable=False, server_default='0'),
    Column('sorttime', WeasylTimestampColumn(), nullable=False),
    Column('fave_count', Integer(), nullable=False, server_default='0'),
    default_fkey(['userid'], ['login.userid'], name='submission_userid_fkey'),
    default_fkey(['folderid'], ['folder.folderid'], name='submission_folderid_fkey'),
)

Index('ind_submission_folderid', submission.c.folderid)
Index('ind_submission_userid_unixtime', submission.c.userid, submission.c.unixtime.desc())
Index('ind_submission_userid', submission.c.userid)
Index('ind_submission_userid_folderid', submission.c.userid, submission.c.folderid)


submission_media_links = Table(
    'submission_media_links', metadata,
    Column('linkid', Integer(), primary_key=True, nullable=False),
    Column('mediaid', Integer(), nullable=False),
    Column('submitid', Integer(), nullable=False),
    Column('link_type', String(length=32), nullable=False),
    Column('attributes', JSONValuesColumn(), nullable=False, server_default=text(u"''::hstore")),
    default_fkey(['submitid'], ['submission.submitid'], name='submission_media_links_submitid_fkey'),
    default_fkey(['mediaid'], ['media.mediaid'], name='submission_media_links_mediaid_fkey'),
)

Index('ind_submission_media_links_submitid', submission_media_links.c.submitid)
Index('ind_submission_media_links_mediaid', submission_media_links.c.mediaid, unique=False)


suspension = Table(
    'suspension', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('reason', Text(), nullable=False),
    Column('release', Integer(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='suspension_userid_fkey'),
)


tag_updates = Table(
    'tag_updates', metadata,
    Column('updateid', Integer(), primary_key=True),
    Column('submitid', Integer(), nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('added', ARRAY(Text())),
    Column('removed', ARRAY(Text())),
    Column('updated_at', Integer(), nullable=False,
           server_default=text(u"(date_part('epoch'::text, now()) - (18000)::double precision)")),
    default_fkey(['submitid'], ['submission.submitid'], name='tag_updates_submitid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='tag_updates_userid_fkey'),
)


user_media_links = Table(
    'user_media_links', metadata,
    Column('linkid', Integer(), primary_key=True, nullable=False),
    Column('mediaid', Integer(), nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('link_type', String(length=32), nullable=False),
    Column('attributes', JSONValuesColumn(), nullable=False, server_default=text(u"''::hstore")),
    default_fkey(['userid'], ['login.userid'], name='user_media_links_userid_fkey'),
    default_fkey(['mediaid'], ['media.mediaid'], name='user_media_links_mediaid_fkey'),
)

Index('ind_user_media_links_submitid', user_media_links.c.userid)
Index('ind_user_media_links_userid', user_media_links.c.userid)
Index('ind_user_media_links_mediaid', user_media_links.c.mediaid, unique=False)


user_links = Table(
    'user_links', metadata,
    Column('linkid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('link_type', String(length=64), nullable=False),
    Column('link_value', String(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='user_links_userid_fkey'),
)

Index('ind_user_links_userid', user_links.c.userid)


user_streams = Table(
    'user_streams', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('start_time', WeasylTimestampColumn(), nullable=False),
    Column('end_time', WeasylTimestampColumn(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='user_streams_userid_fkey'),
)

Index('ind_user_streams_end', user_streams.c.end_time)
Index('ind_user_streams_end_time', user_streams.c.end_time)


user_timezones = Table(
    'user_timezones', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('timezone', String(length=255), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='user_timezones_userid_fkey'),
)


useralias = Table(
    'useralias', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('alias_name', String(length=40), primary_key=True, nullable=False),
    Column('settings', String(), nullable=False, server_default=''),
    default_fkey(['userid'], ['login.userid'], name='useralias_userid_fkey'),
)


userinfo = Table(
    'userinfo', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('birthday', WeasylTimestampColumn(), nullable=False),
    Column('gender', String(length=25), nullable=False, server_default=''),
    Column('country', String(length=50), nullable=False, server_default=''),
    default_fkey(['userid'], ['login.userid'], name='userinfo_userid_fkey'),
)


userpremium = Table(
    'userpremium', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('terms', SMALLINT(), nullable=False),
    default_fkey(['userid'], ['login.userid'], name='userpremium_userid_fkey'),
)


userstats = Table(
    'userstats', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('page_views', Integer(), nullable=False, server_default='0'),
    Column('submit_views', Integer(), nullable=False, server_default='0'),
    Column('followers', Integer(), nullable=False, server_default='0'),
    Column('faved_works', Integer(), nullable=False, server_default='0'),
    Column('journals', Integer(), nullable=False, server_default='0'),
    Column('submits', Integer(), nullable=False, server_default='0'),
    Column('characters', Integer(), nullable=False, server_default='0'),
    Column('collects', Integer(), nullable=False, server_default='0'),
    Column('faves', Integer(), nullable=False, server_default='0'),
    default_fkey(['userid'], ['login.userid'], name='userstats_userid_fkey'),
)


views = Table(
    'views', metadata,
    Column('viewer', String(length=127), primary_key=True, nullable=False),
    Column('targetid', Integer(), primary_key=True, nullable=False),
    Column('type', Integer(), primary_key=True, nullable=False),
)


watchuser = Table(
    'watchuser', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('otherid', Integer(), primary_key=True, nullable=False),
    Column('settings', String(length=20), nullable=False),
    Column('unixtime', Integer(), nullable=False,
           server_default=text(u"(date_part('epoch'::text, now()) - (18000)::double precision)")),
    default_fkey(['otherid'], ['login.userid'], name='watchuser_otherid_fkey'),
    default_fkey(['userid'], ['login.userid'], name='watchuser_userid_fkey'),
)

Index('ind_watchuser_userid', watchuser.c.userid)
Index('ind_watchuser_settings', watchuser.c.settings)
Index('ind_watchuser_userid_settings', watchuser.c.userid, watchuser.c.settings)
Index('ind_watchuser_otherid', watchuser.c.otherid)
Index('ind_watchuser_otherid_settings', watchuser.c.otherid, watchuser.c.settings)


welcome = Table(
    'welcome', metadata,
    Column('welcomeid', Integer(), primary_key=True, nullable=False),
    Column('userid', Integer(), nullable=False),
    Column('otherid', Integer(), nullable=False),
    Column('referid', Integer(), nullable=False, server_default='0'),
    Column('targetid', Integer(), nullable=False, server_default='0'),
    Column('unixtime', WeasylTimestampColumn(), nullable=False),
    Column('type', Integer(), nullable=False),
    Column('deleted', ArrowColumn()),
    default_fkey(['userid'], ['login.userid'], name='welcome_userid_fkey'),
)

Index('ind_welcome_otherid', welcome.c.otherid)
Index('ind_welcome_referid', welcome.c.referid)
Index('ind_welcome_targetid', welcome.c.targetid)
Index('ind_welcome_type', welcome.c.type)
Index('ind_welcome_unixtime', welcome.c.unixtime)
Index('ind_welcome_userid_type', welcome.c.userid, welcome.c.type)


welcomecount = Table(
    'welcomecount', metadata,
    Column('userid', Integer(), primary_key=True, nullable=False),
    Column('journal', Integer(), nullable=False, server_default='0'),
    Column('submit', Integer(), nullable=False, server_default='0'),
    Column('notify', Integer(), nullable=False, server_default='0'),
    Column('comment', Integer(), nullable=False, server_default='0'),
    Column('note', Integer(), nullable=False, server_default='0'),
    default_fkey(['userid'], ['login.userid'], name='welcomecount_userid_fkey'),
)

Index('ind_welcomecount_userid', welcomecount.c.userid)
