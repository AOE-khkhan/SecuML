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

from . import TestConfFactory
from .SeveralFoldsTestConf import SeveralFoldsTestConf


class CvConf(SeveralFoldsTestConf):

    def __init__(self, logger, alerts_conf, num_folds):
        SeveralFoldsTestConf.__init__(self, logger, alerts_conf, num_folds)
        self.method = 'cv'

    def get_exp_name(self):
        name = '__Test_Cv_%d' % (self.num_folds)
        name += SeveralFoldsTestConf.get_exp_name(self)
        return name

    @staticmethod
    def generateParser(parser):
        parser.add_argument('--num-folds-val',
                            type=int,
                            default=4,
                            help='Number of cross validation folds. '
                                 'Default: 4.')

    @staticmethod
    def fromArgs(args, logger):
        alerts_conf = SeveralFoldsTestConf.alertConfFromArgs(args, logger)
        return CvConf(logger, alerts_conf, args.num_folds_val)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = SeveralFoldsTestConf.alertConfFromJson(obj, logger)
        return CvConf(logger, alerts_conf, obj['num_folds'])



TestConfFactory.getFactory().registerClass('CvConf', CvConf)
