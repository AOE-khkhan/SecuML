# SecuML
# Copyright (C) 2016-2019  ANSSI
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

import pandas as pd
import random

from secuml.core.data import labels_tools
from secuml.core.tools.matrix import sort_data_frame


class Cluster(object):

    def __init__(self):
        self.instances_ids = []
        self.distances = []
        self.label = None
        self.clusters_families_stats = {}
        self.num_annotated_instances = 0

    def num_instances(self):
        return len(self.instances_ids)

    def add_instance(self, instance_id, distance, label, family, annotated):
        self.instances_ids.append(instance_id)
        self.distances.append(distance)
        label = labels_tools.label_bool_to_str(label)
        if family is not None:
            key = label + '__' + family
            if key not in self.clusters_families_stats:
                self.clusters_families_stats[key] = 0
            self.clusters_families_stats[key] += 1
        if annotated:
            self.num_annotated_instances += 1

    def final_computation(self, unknown_cluster_id):
        unknown_cluster_id = self.set_label(unknown_cluster_id)
        if self.num_instances() != 0:
            self.sort_instances()
        return unknown_cluster_id

    # The list of instances in the cluster are sorted according to their
    # distance from the centroid
    def sort_instances(self):
        df = pd.DataFrame({'distance': self.distances},
                          index=list(map(str, self.instances_ids)))
        sort_data_frame(df, 'distance', True, True)
        self.instances_ids = list(map(int, df.index.values.tolist()))
        self.distances = df.distance.tolist()

    def set_label(self, unknown_cluster_id):
        max_occurrences = 0
        for key, v in self.clusters_families_stats.items():
            if v > max_occurrences:
                max_occurrences = v
                self.label = key
        if self.label is None:
            self.label = 'unknown_' + str(unknown_cluster_id)
            return unknown_cluster_id + 1
        else:
            return unknown_cluster_id

    def get_label(self):
        return self.label

    # c: center
    # e: edge (does not return instances from the center)
    # r: random (does not return instances from the center and the edge)
    # An instance cannot be in two sets among c, e and r.
    def get_cluster_instances_visu(self, num_instances, rand=False,
                                   drop_instances=None):
        if drop_instances is None:
            drop_instances = []
        num_center = int(num_instances / 2)
        num_edge = num_instances - num_center
        c_e_r = {}
        c_e_r['c'] = self.get_instances('center', num_center,
                                        drop_instances=drop_instances)
        c_e_r['e'] = self.get_instances(
                'anomalous', num_edge,
                drop_instances=drop_instances + c_e_r['c'])
        if rand:
            num_random = num_instances
            c_e_r['r'] = self.get_instances(
                    'random', num_random,
                    drop_instances=drop_instances + c_e_r['c'] + c_e_r['e'])
        else:
            c_e_r['r'] = []
        return c_e_r

    def to_json(self, drop_instances=None):
        obj = {}
        if drop_instances is None:
            obj['instances_ids'] = self.instances_ids
            obj['distances'] = self.distances
        else:
            obj['instances_ids'] = []
            obj['distances'] = []
            for i in range(len(self.instances_ids)):
                instance_id = self.instances_ids[i]
                if instance_id in drop_instances:
                    continue
                else:
                    obj['instances_ids'].append(instance_id)
                    obj['distances'].append(self.distances[i])
        obj['label'] = self.label
        return obj

    @staticmethod
    def from_json(obj):
        cluster = Cluster()
        cluster.instances_ids = obj['instances_ids']
        cluster.distances = obj['distances']
        cluster.label = obj['label']
        return cluster

    def get_instances(self, c_e_r, num_instances, drop_instances=None):
        if c_e_r == 'all':
            return self.instances_ids
        if num_instances == 0:
            return []
        if drop_instances is None:
            instances = self.instances_ids
        else:
            instances = [
                x for x in self.instances_ids if x not in drop_instances]
        if len(instances) < num_instances:
            return instances
        if c_e_r == 'center':
            return instances[:num_instances]
        elif c_e_r == 'anomalous':
            return instances[-num_instances:]
        elif c_e_r == 'random':
            return random.sample(instances, num_instances)
        else:
            raise ValueError('Invalid argument value c_e_r %s' % (c_e_r))
