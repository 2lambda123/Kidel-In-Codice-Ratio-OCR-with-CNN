import db_connection_handler as db
import image_utils as imgutil
import os
import random

ROOT_FOLDER = 'not_code/datasets/2016-12-10'
NEG_WIDTH_FOLDER = '/neg_width'
TOO_WIDE = 'wide'
TOO_NARROW = 'narrow'

def parse_coords_from_path(path):
    filename = path.split('/')[len(path.split('/'))-1].split('.')[0]
    width, y, x = filename.split('_')
    return (int(x), int(y))

def get_positive_samples_coordinates_and_page(char, as_dict=False):
    """
        returns: (x, y, width, height, page) if as_dict is False
        {'page': [(x, y, width, height)]} otherwise
    """
    nt = 'nt%'
    rum = 'rum%'
    char_match = char + '%'
    query = """
        SELECT image.path, image.page, image.width, image.height
        FROM majority_voting_three_votes as mvt, image
        WHERE mvt.transcription like %s AND
            NOT (mvt.transcription like %s OR mvt.transcription like %s) AND
            image.id = mvt.image_id;
    """
    q_result = db.execute_query(query, (char_match, nt, rum))
    coordinates = [parse_coords_from_path(res[0])+(res[2], res[3], res[1]) for res in q_result]

    if as_dict:
        by_page = {}
        for x, y, w, h, page in coordinates:
            try:
                by_page[page].append((x,y,w,h))
            except KeyError:
                by_page[page] = []
                by_page[page].append((x,y,w,h))
        coordinates = by_page

    return coordinates

def get_all_positive_samples_by_char(char, root_folder=ROOT_FOLDER):
    """
        ottiene una lista di esempi positivi per un certo carattere.
        1) query al db dei path
        2) estrazione delle immagini
        3) ritorna come numpy array
    """
    nt = 'nt%'
    rum = 'rum%'
    char_match = char + '%'

    query = """
        SELECT mvt.path
        FROM majority_voting_three_votes as mvt
        WHERE mvt.transcription like %s AND
            NOT (mvt.transcription like %s OR mvt.transcription like %s);
    """
    samples_paths = db.execute_query(query, (char_match, nt, rum))
    complete_paths = [root_folder+sp[0] for sp in samples_paths]

    return imgutil.open_many_samples(complete_paths)


def get_n_negative_samples_by_width_and_char(char, samples_n, char_width=None, root_folder=ROOT_FOLDER, verbose = 1):
    path = ROOT_FOLDER + NEG_WIDTH_FOLDER + '/' + char
    tw_path = path + '/too_wide/'
    tn_path = path + '/too_narrow/'
    samples_paths = []

    if char_width == TOO_WIDE:
        filenames = [tw_path + f for f in os.listdir(tw_path)]
        if samples_n > len(filenames) and verbose:
            print('[WARNING]: ci sono meno campioni troppo ampi di quelli richiesti. Trovati:', len(filenames))
        samples_paths += filenames[:samples_n]
    elif char_width == TOO_NARROW:
        filenames = [tn_path + f for f in os.listdir(tn_path)]
        if samples_n > len(filenames) and verbose:
            print('[WARNING]: ci sono meno campioni troppo stretti di quelli richiesti. Trovati:', len(filenames))
        samples_paths += filenames[:samples_n]
    else: #fornisce entrambi gli esempi nella stessa quantità
        tw_filenames = [tw_path + f for f in os.listdir(tw_path)]
        tn_filenames = [tn_path + f for f in os.listdir(tn_path)]
        if samples_n > len(tw_filenames) and verbose:
            print('[WARNING]: ci sono meno campioni troppo ampi di quelli richiesti. Trovati:', len(tw_filenames))
        if samples_n > len(tn_filenames) and verbose:
            print('[WARNING]: ci sono meno campioni troppo stretti di quelli richiesti. Trovati:', len(tn_filenames))
        samples_paths += tw_filenames[:samples_n] + tn_filenames[:samples_n]

    return imgutil.open_many_samples(samples_paths)


def get_n_negative_samples_by_height_and_char(char, char_image_type, samples_n, root_folder=ROOT_FOLDER):
    img_type = char_image_type.lower()
    type1_n = samples_n/2
    rest = samples_n%2
    type2_n = samples_n - (type1_n + rest)

    query = """
        SELECT setseed(0.5);
        SELECT *
        FROM
        	( SELECT DISTINCT image.path
        	FROM image
        	WHERE image.type = %s
        	) as samples
        ORDER BY random()
        LIMIT %s;
    """
    samples_paths = []

    if img_type == 'alto':
        mid_paths = db.execute_query(query, ('centrato',type1_n))
        low_paths = db.execute_query(query, ('basso',type2_n))
        samples_paths = mid_paths + low_paths
    elif img_type == 'basso':
        mid_paths = db.execute_query(query, ('centrato',type1_n))
        high_paths = db.execute_query(query, ('alto',type2_n))
        samples_paths = mid_paths + high_paths
    else:
        low_paths = db.execute_query(query, ('basso',type1_n))
        high_paths = db.execute_query(query, ('alto',type2_n))
        samples_paths = low_paths + high_paths

    complete_paths = [root_folder+sp[0] for sp in samples_paths]

    return imgutil.open_many_samples(complete_paths)


def get_n_negative_labeled_samples_by_char(char, samples_n, root_folder=ROOT_FOLDER):
    """
        ottiene la lista di samples negativi etichettati negativamente
        con + di tre voti.
        samples_n poiche' la quantita' e' decisa sulla base degli esempi positivi.
        1) query al db dei path
        2) lista di immagini
        3) numpy array
    """
    nt = 'nt%'
    rum = 'rum%'
    char_match = char + '%'

    query = """
        SELECT setseed(0.5);
        SELECT *
        FROM
            (SELECT DISTINCT image.path
            FROM symbol, job, task, result, image
            WHERE image.id = result.image_id AND
                symbol.id = job.symbol_id AND
                job.id = task.job_id AND
                task.id = result.task_id AND
                symbol.transcription like %s AND
                NOT (symbol.transcription like %s OR symbol.transcription like %s) AND
                result.answer::text = 'No'::text
            GROUP BY result.image_id, symbol.transcription, image.path, symbol.id
            HAVING count(*) >= 3) as neg_samples
        ORDER BY random()
        LIMIT %s;
    """

    samples_paths = db.execute_query(query, (char_match, nt, rum, samples_n))

    complete_paths = [root_folder+sp[0] for sp in samples_paths]

    return imgutil.open_many_samples(complete_paths)
