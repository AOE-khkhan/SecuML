# SecuML
# Copyright (C) 2016-2018  ANSSI
#
# SecuML is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# SecuML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from SecuML.core.data import labels_tools

from SecuML.exp.conf.AnnotationsConf import AnnotationsTypes
from SecuML.exp.db_tables import AnnotationsAlchemy
from SecuML.exp.db_tables import GroundTruthAlchemy


def getAnnotation(session, annotations_type, annotations_id, dataset_id,
                  instance_id):
    if annotations_type == AnnotationsTypes.partial:
        return getInstancePartialAnnotation(session, annotations_id,
                                            instance_id)
    elif annotations_type == AnnotationsTypes.ground_truth:
        return getInstanceGroundTruth(session, dataset_id, instance_id)
    else:
        return None


def getInstancePartialAnnotationRow(session, annotations_id, instance_id):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.filter(AnnotationsAlchemy.instance_id == int(instance_id))
    try:
        return query.one()
    except NoResultFound:
        return None


def getInstancePartialAnnotation(session, annotations_id, instance_id):
    row = getInstancePartialAnnotationRow(session, annotations_id, instance_id)
    if row is None:
        return None
    else:
        return row.label, row.family


def getInstanceGroundTruth(session, dataset_id, instance_id):
        query = session.query(GroundTruthAlchemy)
        query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
        query = query.filter(GroundTruthAlchemy.instance_id == int(instance_id))
        try:
            row = query.one()
            return row.label, row.family
        except NoResultFound:
            return None


def getGroundTruth(session, dataset_id):
    query = session.query(GroundTruthAlchemy)
    query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
    query = query.order_by(GroundTruthAlchemy.instance_id)
    res = query.all()
    labels = [labels_tools.labelStringToBoolean(r.label) for r in res]
    families = [r.family for r in res]
    return labels, families


def getAnnotatedInstances(session, annotations_id):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    return [(r.instance_id, r.label, r.family) for r in query.all()]


def datasetHasFamilies(session, annotations_id):
    families = getDatasetFamilies(session, annotations_id)
    if len(families) == 0:
        return False
    if len(families) == 1:
        return families[0] != 'other'
    return True


def getDatasetFamilies(session, annotations_id):
    query = session.query(AnnotationsAlchemy.family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.distinct(AnnotationsAlchemy.family)
    families = [r.family for r in query.all()]
    return families


def get_labels_families(session, annotations_type, annotations_id, dataset_id,
                        instance_ids=None, iter_max=None):
    if annotations_type == AnnotationsTypes.none:
        return {}
    elif annotations_type == AnnotationsTypes.ground_truth:
        query = get_labels_families_gt(session, dataset_id, instance_ids)
    elif annotations_type == AnnotationsTypes.partial:
        query = get_labels_families_partial(session, annotations_id,
                                            instance_ids, iter_max)
    else:
        assert(False)
    labels = {}
    for r in query.all():
        if r.label not in list(labels.keys()):
            labels[r.label] = {}
        labels[r.label][r.family] = 0
    return labels


def get_labels_families_gt(session, dataset_id, instance_ids):
    query = session.query(GroundTruthAlchemy)
    query = query.distinct(GroundTruthAlchemy.label, GroundTruthAlchemy.family)
    query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
    if instance_ids is not None:
        query = query.filter(GroundTruthAlchemy.instance_id.in_(instance_ids))
    return query


def get_labels_families_partial(session, annotations_id, instance_ids,
                                iter_max):
    query = session.query(AnnotationsAlchemy)
    query = query.distinct(AnnotationsAlchemy.label, AnnotationsAlchemy.family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iter_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iter_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    return query


def get_label_family_ids(session, annotations_type, annotations_id, dataset_id,
                         label, family=None, iter_max=None, instance_ids=None):
    if annotations_type == AnnotationsTypes.none:
        return []
    elif annotations_type == AnnotationsTypes.ground_truth:
        return get_label_family_ids_gt(session, dataset_id, label, family,
                                       instance_ids)
    elif annotations_type == AnnotationsTypes.partial:
        return get_label_family_ids_partial(session, annotations_id, label,
                                            family, iter_max, instance_ids)
    else:
        assert(False)


def get_label_family_ids_partial(session, annotations_id, label, family,
                                 iter_max, instance_ids):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.filter(AnnotationsAlchemy.label == label)
    if family is not None:
        query = query.filter(AnnotationsAlchemy.family == family)
    if iter_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iter_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    return [r.instance_id for r in query.all()]


def get_label_family_ids_gt(session, dataset_id, label, family, instance_ids):
    query = session.query(GroundTruthAlchemy)
    query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
    query = query.filter(GroundTruthAlchemy.label == label)
    if family is not None:
        query = query.filter(GroundTruthAlchemy.family == family)
    if instance_ids is not None:
        query = query.filter(GroundTruthAlchemy.instance_id.in_(instance_ids))
    return [r.instance_id for r in query.all()]

def getUnlabeledIds(session, annotations_type, annotations_id, instance_ids):
    if instance_ids is None:
        assert(False)
    if annotations_type == AnnotationsTypes.ground_truth:
        return []
    annotated_instances = map(lambda x: x[0],
                              getAnnotatedInstances(session, annotations_id))
    return list(set(instance_ids) - set(annotated_instances))


def getFamiliesCounts(session, annotations_id, iter_max=None, label=None):
    query = session.query(AnnotationsAlchemy.family,
                          func.count(AnnotationsAlchemy.family))
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iter_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iter_max)
    if label is not None:
        query = query.filter(AnnotationsAlchemy.label == label)
    query = query.group_by(AnnotationsAlchemy.family)
    family_counts = {}
    for r in query.all():
        family_counts[r[0]] = r[1]
    return family_counts


def addAnnotation(session, annotations_id, instance_id, label, family,
                  iteration_number, method):
    annotation = AnnotationsAlchemy(annotations_id=annotations_id,
                                    # MySQL does not support numpy types (int64)
                                    instance_id=int(instance_id),
                                    label=label,
                                    family=family,
                                    iteration=iteration_number,
                                    method=method)
    session.add(annotation)
    session.flush()


def updateAnnotation(session, annotations_id, instance_id, label, family,
                     iteration_number, method):
    row = getInstancePartialAnnotationRow(session, annotations_id, instance_id)
    if row is None:
        addAnnotation(session, annotations_id, instance_id, label, family,
                      iteration_number, method)
    else:
        row.label = label
        row.family = family
        row.iteration = iteration_number
        row.method = method
        session.flush()


def removeAnnotation(session, annotations_id, instance_id):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.instance_id == instance_id)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    try:
        label = query.one()
        session.delete(label)
        session.flush()
    except NoResultFound:
        return None


def changeFamilyName(session, annotations_id, label, family, new_family):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.label == label)
    query = query.filter(AnnotationsAlchemy.family == family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    instances = query.all()
    for instance in instances:
        instance.family = new_family
    session.flush()


def changeFamilyLabel(session, annotations_id, label, family):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.label == label)
    query = query.filter(AnnotationsAlchemy.family == family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    instances = query.all()
    bool_label = labels_tools.labelStringToBoolean(label)
    new_label = labels_tools.labelBooleanToString(not bool_label)
    for instance in instances:
        instance.label = new_label
    session.flush()


def mergeFamilies(session, annotations_id, label, families, new_family):
    for family in families:
        changeFamilyName(session, annotations_id, label, family, new_family)
