#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2013 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#
#

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


# =====================================================================
# Continuous
# =====================================================================
from wndcharm.ArtificialFeatureSets import CreateArtificialFeatureSet_Continuous
from wndcharm.FeatureSet import ContinuousClassificationExperimentResult,\
				ContinuousFeatureWeights

class TESTINGContinuousClassificationExperimentResult( unittest.TestCase ):
	"""Test various functions from the DiscreteClassificationExperimentResult class."""

	# ---------------------------------------------------------------------
	def test_NewShuffleSplitLeastSquares(self):
		"""CONTINUOUS SHUFFLE SPLIT LEAST SQUARES"""

		fs_kwargs = {}
		fs_kwargs['name'] = "CONTINUOUS PerSampleStatistics_TESTFS"
		fs_kwargs['n_samples'] = 100
		fs_kwargs['num_features_per_signal_type'] = 5
		fs_kwargs['noise_gradient'] = 5
		fs_kwargs['initial_noise_sigma'] = 5
		fs_kwargs['n_samples_per_group'] = 1
		fs_kwargs['random_state'] = 43

		fs = CreateArtificialFeatureSet_Continuous( **fs_kwargs )

		ss_kwargs = {}
		ss_kwargs['n_iter'] = 25
		ss_kwargs['name'] = "Continuous Shuffle Split Least Squares POSITIVE CONTROL"
		ss_kwargs['quiet'] = True
		ss_kwargs['random_state'] = 43
		exp = ContinuousClassificationExperimentResult.NewShuffleSplit( fs, **ss_kwargs )

		exp.GenerateStats()

		# len( exp ) is supposed to be the number of batch results (split results)
		self.assertIs( len(exp), ss_kwargs['n_iter'] )

		# Positive control - Artificial data with defaults should corellate almost perfectly
		self.assertAlmostEqual( exp.pearson_coeff, 1.0, delta=0.02 )

		# Negative control - take the bottom quintile of the artificial features
		# which ARE functions of ground truth but should score low on linear correlation,
		# e.g., sin, x^2, etc.
		max_allowable_pearson_coeff = 0.35

		temp_normalized_fs = fs.Normalize( inplace=False )
		ranked_nonzero_features = \
		  ContinuousFeatureWeights.NewFromFeatureSet( temp_normalized_fs ).Threshold(_all='nonzero')

		quintile = int( len( ranked_nonzero_features ) / 5 )
		crappy_features = ranked_nonzero_features.Slice( quintile*4, len( ranked_nonzero_features ) )
		#crappy_features.Print()
		crap_featureset = fs.FeatureReduce( crappy_features.names )

		ss_kwargs['name'] = "Continuous Shuffle Split Least Squares NEGATIVE CONTROL"
		exp = ContinuousClassificationExperimentResult.NewShuffleSplit( crap_featureset, **ss_kwargs )
		exp.GenerateStats()
		exp.PerSampleStatistics()
		self.assertAlmostEqual( exp.pearson_coeff, 0.0, delta=max_allowable_pearson_coeff )

	# --------------------------------------------------------------------
	def test_NewShuffleSplitVoting(self):
		"""CONTINUOUS SHUFFLE SPLIT VOTING METHOD"""

		fs_kwargs = {}
		fs_kwargs['name'] = "CONTINUOUS PerSampleStatistics_TESTFS"
		fs_kwargs['n_samples'] = 100
		fs_kwargs['num_features_per_signal_type'] = 5
		fs_kwargs['noise_gradient'] = 5
		fs_kwargs['initial_noise_sigma'] = 5
		fs_kwargs['n_samples_per_group'] = 1
		fs_kwargs['random_state'] = 43

		fs = CreateArtificialFeatureSet_Continuous( **fs_kwargs )

		ss_kwargs = {}
		ss_kwargs['n_iter'] = 25
		ss_kwargs['name'] = "Continuous Shuffle Split Voting-Regression POSITIVE CONTROL"
		ss_kwargs['quiet'] = True
		ss_kwargs['random_state'] = 43
		ss_kwargs['classifier'] = 'voting'
		exp = ContinuousClassificationExperimentResult.NewShuffleSplit( fs, **ss_kwargs )

		exp.GenerateStats()

		self.assertIs( len(exp), ss_kwargs['n_iter'] )

		# Positive control - Artificial data with defaults should corellate almost perfectly
		self.assertAlmostEqual( exp.pearson_coeff, 1.0, delta=0.02 )

		# Negative control - take the bottom quintile of the artificial features
		# which ARE functions of ground truth but should score low on linear correlation,
		# e.g., sin, x^2, etc.
		max_allowable_pearson_coeff = 0.30

		temp_normalized_fs = fs.Normalize( inplace=False )
		ranked_nonzero_features = \
		  ContinuousFeatureWeights.NewFromFeatureSet( temp_normalized_fs ).Threshold(_all='nonzero')

		quintile = int( len( ranked_nonzero_features ) / 5 )
		crappy_features = ranked_nonzero_features.Slice( quintile*4, len( ranked_nonzero_features ) )
		#crappy_features.Print()
		crap_featureset = fs.FeatureReduce( crappy_features.names )

		ss_kwargs['name'] = "Continuous Shuffle Split Voting-Regression NEGATIVE CONTROL",
		exp = ContinuousClassificationExperimentResult.NewShuffleSplit( crap_featureset, **ss_kwargs )
		exp.GenerateStats()
		self.assertAlmostEqual( exp.pearson_coeff, 0.0, delta=max_allowable_pearson_coeff )

	# -------------------------------------------------------------------
	def test_PerSampleStatistics(self):
		"""Testing ContinuousClassificationExperimentResult.PerSampleStatistics()

		Goal is to check the aggregating functionality of PerSampleStatistics"""

		# create a small FeatureSet with not a lot of samples and not a lot of features
		# to enable quick classification

		fs_kwargs = {}
		fs_kwargs['name'] = "CONTINUOUS PerSampleStatistics_TESTFS"
		fs_kwargs['n_samples'] = n_samples = 20
		fs_kwargs['num_features_per_signal_type'] = 2 # small on purpose, to make test fast
		fs_kwargs['noise_gradient'] = 25
		fs_kwargs['initial_noise_sigma'] = 75
		fs_kwargs['n_samples_per_group'] = 1
		fs_kwargs['random_state'] = 42
		fs = CreateArtificialFeatureSet_Continuous( **fs_kwargs )

		ss_kwargs = {}
		ss_kwargs['name'] = "Continuous PerSampleStatistics ShuffleSplit"
		ss_kwargs['quiet'] = True
		ss_kwargs['n_iter'] = n_iter = 50 # do a lot of iterations so that all samples will be hit
		ss_kwargs['train_size'] = train_size = 16
		ss_kwargs['test_size' ] = test_size = 4
		ss_kwargs['random_state'] = 42
		exp = ContinuousClassificationExperimentResult.NewShuffleSplit( fs, **ss_kwargs )

		exp.GenerateStats()

		# Capture output from PerSampleStatistics
		from StringIO import StringIO
		out = StringIO()
		try:
				exp.PerSampleStatistics( output_stream=out )
		except Exception as e:
				m = 'Error in experiment.PredictedValueAnalysis: %s' % e
				message += m + '\n'
				self.fail( m )

		# Count the number of lines
		# 3 header lines + 2*num_samples + n_iter*test_size
		per_sample_output = out.getvalue().splitlines()
		self.assertEqual( len(per_sample_output), 3 + 2*n_samples + n_iter*test_size )

# =====================================================================
# Discrete
# =====================================================================
from wndcharm.ArtificialFeatureSets import CreateArtificialFeatureSet_Discrete
from wndcharm.FeatureSet import FeatureSet_Discrete, DiscreteClassificationExperimentResult

class TESTINGDiscreteClassificationExperimentResult( unittest.TestCase ):
	"""Test various functions from the DiscreteClassificationExperimentResult class."""
	
	# -------------------------------------------------------------------
	def test_PerSampleStatisticsWITHOUTPredictedValue(self):
		"""DISCRETE ShuffleSplit/PerSampleStatistics w/ no predicted value"""

		# CAN'T USE THIS, SINCE THE CLASS NAMES ARE INTERPOLATABLE
		# 2-class, 10 samples per class
		#fs = FeatureSet_Discrete.NewFromFitFile( '../wndchrm_tests/test-l.fit' )

		fs_kwargs = {}
		fs_kwargs['name'] = "DISCRETE PerSampleStatistics_TESTFS"
		fs_kwargs['n_samples'] = n_samples = 20
		fs_kwargs['n_classes'] = 2
		fs_kwargs['num_features_per_signal_type'] = 2 # small on purpose, to make test fast
		fs_kwargs['noise_gradient'] = 25
		fs_kwargs['initial_noise_sigma'] = 75
		fs_kwargs['n_samples_per_group'] = 1
		fs_kwargs['random_state'] = 42
		fs_kwargs['interpolatable'] = False
		fs = CreateArtificialFeatureSet_Discrete( **fs_kwargs )


		ss_kwargs = {}
		ss_kwargs['name'] = "Discrete PerSampleStatistics ShuffleSplit"
		ss_kwargs['quiet'] = True
		ss_kwargs['n_iter'] = n_iter = 5
		ss_kwargs['train_size'] = train_size = 8 # per-class
		ss_kwargs['test_size' ] = test_size = 2 # per-class
		ss_kwargs['random_state'] = 42
		exp = DiscreteClassificationExperimentResult.NewShuffleSplit( fs, **ss_kwargs )
		exp.PerSampleStatistics()
		self.assertTrue(True)

	# -------------------------------------------------------------------
	def test_PerSampleStatisticsWITHPredictedValue(self):
		"""DISCRETE PerSampleStatistics with numeric predicted value"""

		fs = CreateArtificialFeatureSet_Discrete( n_samples=10,
         n_classes=2, num_features_per_signal_type=50, noise_gradient=25,
         initial_noise_sigma=75, random_state=42 )
		exp = DiscreteClassificationExperimentResult.NewShuffleSplit(
		                                                fs, quiet=True, random_state=42 )
		exp.PerSampleStatistics()
		self.assertTrue(True)


if __name__ == '__main__':
		unittest.main()
