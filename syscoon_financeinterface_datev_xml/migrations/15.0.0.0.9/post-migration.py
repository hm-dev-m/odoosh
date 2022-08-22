def migrate(cr, version):
    import logging

    _logger = logging.getLogger(__name__)

    _logger.info('post_init: Start')

    COMPUTED_FIELDS = {
        'account.move': [
            'commercial_partner_id',
        ],
    }


    def imd_custom_model_name(model):
        return '%s_model' % model.partition('x_')[-1]

    # Call compute methods
    for modelname, model_data in COMPUTED_FIELDS.items():
        recompute_fields(cr, modelname, model_data, _logger)

    _logger.info('post_init: End')


def env(cr):
    try:
        from odoo.api import Environment
        from odoo import SUPERUSER_ID
    except ImportError:
        pass
    return Environment(cr, SUPERUSER_ID, {})


def recompute_fields(cr, model, fields, logger, ids=None, chunk_size=256):
    from operator import itemgetter

    if ids is None:
        cr.execute('SELECT id FROM "%s"' % model.replace('.', '_'))
        ids = tuple(map(itemgetter(0), cr.fetchall()))

    Model = env(cr)[model]
    size = (len(ids) + chunk_size - 1) / chunk_size
    qual = '%s %d-bucket' % (model, chunk_size) if chunk_size != 1 else model
    for subids in log_progress(chunks(ids, chunk_size, list), logger, qualifier=qual, size=size):
        records = Model.browse(subids)
        for field in fields:
            env(cr).add_to_compute(Model._fields[field], Model.search([]))

def log_progress(it, logger, qualifier='elements', size=None):
    import datetime
    if size is None:
        size = len(it)
    size = float(size)
    t0 = t1 = datetime.datetime.now()
    for i, e in enumerate(it, 1):
        yield e
        t2 = datetime.datetime.now()
        if (t2 - t1).total_seconds() > 60:
            t1 = datetime.datetime.now()
            tdiff = t2 - t0
            logger.info("[%.02f%%] %d/%d %s processed in %s (TOTAL estimated time: %s)",
                        (i / size * 100.0), i, size, qualifier, tdiff,
                        datetime.timedelta(seconds=tdiff.total_seconds() * size / i))


def chunks(iterable, size, fmt=None):
    from itertools import chain, islice
    if fmt is None:
        fmt = {
            str: ''.join,
            unicode: u''.join,
        }.get(type(iterable), iter)

    it = iter(iterable)
    try:
        while True:
            yield fmt(chain((next(it),), islice(it, size - 1)))
    except StopIteration:
        return
