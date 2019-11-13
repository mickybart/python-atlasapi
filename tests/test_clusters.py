"""
Nose2 Unit Tests for the clusters module.


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from json import dumps
from atlasapi.clusters import AtlasBasicReplicaSet, MongoDBMajorVersion as mdb_version, ClusterConfig
from atlasapi.clusters import ClusterConfig, ProviderSettings, ReplicationSpecs, InstanceSizeName
from atlasapi.clusters import RegionConfig
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ClusterTests(BaseTests):

    def test_00_get_all_clusters(self):
        cluster_list = list(self.a.Clusters.get_all_clusters(iterable=True))

        self.assertTrue(type(cluster_list) is list)
    test_00_get_all_clusters.basic = True

    def test_01_get_all_clusters_type(self):
        cluster_list = list(self.a.Clusters.get_all_clusters(iterable=True))
        for each_cluster in cluster_list:
            logger.warning(each_cluster)
            self.assertTrue(type(each_cluster) is dict)
    test_01_get_all_clusters_type.basic = True

    def test_02_get_a_cluster_as_obj(self):
        cluster = self.a.Clusters.get_single_cluster_as_obj(self.TEST_CLUSTER_NAME)
        self.assertTrue(type(cluster) is ClusterConfig)
        self.assertEqual(cluster.name, self.TEST_CLUSTER_NAME)
    test_02_get_a_cluster_as_obj.basic = True

    def test_03_get_a_cluster(self):
        cluster = self.a.Clusters.get_single_cluster(self.TEST_CLUSTER_NAME)
        self.assertTrue(type(cluster) is dict)
        self.assertEqual(cluster['name'], self.TEST_CLUSTER_NAME)
    test_03_get_a_cluster.basic = True

    def test_04_create_basic_cluster(self):
        myoutput = self.a.Clusters.create_basic_rs(name=self.TEST_CLUSTER2_NAME_UNIQUE, version=mdb_version.v4_2,
                                                   size=InstanceSizeName.M10)
        self.assertEqual(type(myoutput), AtlasBasicReplicaSet)
        pprint(myoutput.config.as_dict())
        print('-------------------Waiting a bit to allow the cluster to be created......-------------')
        sleep(30)
        print('-----------------------------------Done Sleeping -------------------------------------')

    test_04_create_basic_cluster.advanced = True

    def test_05_modify_cluster_disk(self):
        existing = self.a.Clusters.get_single_cluster_as_obj(cluster=self.TEST_CLUSTER_NAME)
        old_size = existing.disk_size_gb
        new_size = existing.disk_size_gb + 1
        existing.disk_size_gb = new_size
        new_config = self.a.Clusters.modify_cluster(self.TEST_CLUSTER_NAME, existing)
        pprint('Old Size: {}.  New Size {}'.format(old_size, new_size))
        self.assertEquals(new_config.get('diskSizeGB', 0), new_size), new_config
        print('-------------------Waiting a bit to allow the cluster to be modified......-------------')
        sleep(20)
        print('-----------------------------------Done Sleeping -------------------------------------')


    def test_06_delete_a_cluster(self):
        myoutput = self.a.Clusters.delete_cluster(cluster=self.TEST_CLUSTER2_NAME_UNIQUE, areYouSure=True)
        print('Successfully Deleted {}, output was '.format(self.TEST_CLUSTER2_NAME_UNIQUE, myoutput))

    test_06_delete_a_cluster.advanced = True

    def test_07_create_a_cluster(self):
        provider_settings: ProviderSettings = ProviderSettings()
        regions_config = RegionConfig()
        replication_specs = ReplicationSpecs(regions_config={provider_settings.region_name: regions_config.__dict__})
        cluster_config = ClusterConfig(name=self.TEST_CLUSTER3_NAME_UNIQUE,
                                       providerSettings=provider_settings,
                                       replication_specs=replication_specs)

        output = self.a.Clusters.create_cluster(cluster_config)
        pprint(output)

    test_07_create_a_cluster.advanced = True

    def test_08_resize_a_cluster(self):
        output = self.a.Clusters.modify_cluster_instance_size(cluster=self.TEST_CLUSTER3_NAME_UNIQUE,
                                                              new_cluster_size=InstanceSizeName.M20)

    test_08_resize_a_cluster.advanced = True

    def test_09_deleted_resized_cluster(self):
        output = self.a.Clusters.delete_cluster(cluster=self.TEST_CLUSTER3_NAME_UNIQUE, areYouSure=True)
        print('Successfully Deleted resized cluster :{}, output was '.format(self.TEST_CLUSTER2_NAME_UNIQUE, output))

    test_09_deleted_resized_cluster.advanced = True

    def test_10_pause_cluster(self):
        pprint('Pausing Cluster {}'.format(self.TEST_CLUSTER_NAME))
        try:
            out = self.a.Clusters.pause_cluster(cluster=self.TEST_CLUSTER_NAME, toggle_if_paused=True)
            self.assertTrue(type(out), dict), "Out Type is {}".format(type(out))
        except Exception as e:
            if e.details.get('errorCode') == 'CANNOT_PAUSE_RECENTLY_RESUMED_CLUSTER':
                print("We are working to fast. {}".format(e.details.get('detail')))
                pass

    test_10_pause_cluster.advanced = True
