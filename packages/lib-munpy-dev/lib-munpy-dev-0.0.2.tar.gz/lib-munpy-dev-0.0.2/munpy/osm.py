import os.path
import json

import requests
from itertools import chain
from typing import Tuple, List

import pandas as pd
from osmium import SimpleHandler

from munpy import config
from munpy.general import findStreets, haversine_distance, dat_to_db


def get_bounding_box(top, left, bottom, right, save_path, address=config.OSM_API, port=5000):
    url = f'http://{address}:{port}/download_box/{top}/{left}/{bottom}/{right}'

    try:
        get_response = requests.get(url)
        if get_response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(get_response.content)
        else:
            print(f'Request failed with status code {get_response.status_code}')

    except Exception as e:
        print(e)


def get_gounding_polygon(name: str, coordinates: List, savepath: str, address=config.OSM_API, port=5000) -> None:
    url = f'http://{address}:{port}/download_polygon'
    content = json.dumps({'name': name, 'area': coordinates})

    try:
        post_response = requests.post(url, data=content, headers={'Content-Type': 'application/json'})
        if post_response.status_code == 200:
            with open(savepath, 'wb') as f:
                f.write(post_response.content)
        else:
            print(f'Request failed with status code {post_response.status_code}')

    except Exception as e:
        print(e)


class OSMHandler(SimpleHandler):
    # Ancho de carril medio en España
    LANE_WIDTH = 3.5
    # Tipos de carretera de OpenStreetMap aceptados {'type': # of lanes}
    HIGHWAY_TYPES = {'primary': 4, 'secondary': 3, 'residential': 2, 'tertiary': 2}
    # Average building heigth in Spain
    BUILDING_HEIGHT = 10.0

    def __init__(self, city):
        SimpleHandler.__init__(self)

        self.city = city
        self.osm_file = os.path.join(config.LEZ_DIR, f'{city}/domain/map.osm')

        self.osm_ways = []
        self.osm_nodes = []

        self.street_df = pd.DataFrame()
        self.intersection_df = pd.DataFrame()

    @staticmethod
    def calculate_way_width(element):
        typo = 1 if element.tags['highway'] == 'primary' else 0

        if 'lanes' in element.tags:
            width = int(element.tags['lanes']) * OSMHandler.LANE_WIDTH
        else:
            width = OSMHandler.HIGHWAY_TYPES[element.tags['highway']]

        intensity = OSMHandler.HIGHWAY_TYPES[element.tags['highway']]

        return width, typo, intensity

    def append_way(self, element):
        # Handle name of the road
        street_name = 'Unknown'
        if 'name' in element.tags:
            street_name = element.tags['name']

        # First check if the way is in the accepted types
        if 'highway' in element.tags and element.tags['highway'] in OSMHandler.HIGHWAY_TYPES:
            way_node_list = [node.ref for node in element.nodes]  # List with the nodes conforming the way
            way_width, typo, intensity = self.calculate_way_width(
                element
            )  # Get way width from its type/number of lanes

            self.osm_ways.append(
                [
                    element.id, way_node_list, way_width,
                    OSMHandler.BUILDING_HEIGHT, typo, intensity, street_name
                ]
            )

    def tag_inventory(self, element, element_type):
        if element_type == 'way':
            self.append_way(element)

        elif element_type == 'node':
            self.osm_nodes.append(
                [
                    element.id, element.location.lon, element.location.lat
                ]
            )

    def node(self, n):
        self.tag_inventory(n, "node")

    def way(self, w):
        self.tag_inventory(w, "way")

    def relation(self, r):
        self.tag_inventory(r, "relation")

    def create_munich_files(self, save=False, merge=False, merge_length=10.0):
        """
        Combines 'create_munich_streets' and 'create_munich_intersections' and finishes the workflow
        :param save: Guardar o no guardar archivo en directorio LEZ
        :param merge: Mergear o no las calles más pequeñas.
        :param merge_length: parámetro min_length de self.merge_streets()
        :return:
        """

        self.apply_file(self.osm_file)
        self._create_munich_streets()
        self._create_munich_intersections()
        self._add_street_length()
        self._reset_intersection_ids()

        if merge:
            self._merge_streets(min_length=merge_length)  # todo: esto está en testing

        if save:
            self.street_df.rename(columns={'street_id': '#id'}).to_csv(
                os.path.join(config.LEZ_DIR, f'{self.city}/domain/street.dat'),
                columns=['#id', 'begin_inter', 'end_inter', 'length', 'width', 'height', 'typo'],
                sep=';', index=False
            )

            self._writeIntersections()

            street_database = dat_to_db(self.street_df, self.intersection_df)
            street_database.to_csv(os.path.join(config.LEZ_DIR, f'{self.city}/domain/street.csv'), index=False)
            self.intersection_df.to_csv(
                os.path.join(config.LEZ_DIR, f'{self.city}/domain/intersection.csv'),
                columns=['node_id', 'lon', 'lat'], index=False
            )

        return self.street_df, self.intersection_df

    def _parse_to_df(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Converts the osm_ways and osm_nodes lists to pandas dataframes.
        :return: dataframes with the data organized
        """
        ways_columns = ['street_id', 'nodes', 'width', 'height', 'typo', 'intensity', 'street_name']
        nodes_columns = ['node_id', 'lon', 'lat']

        ways = pd.DataFrame(self.osm_ways, columns=ways_columns)
        nodes = pd.DataFrame(self.osm_nodes, columns=nodes_columns)

        relevant_nodes = list(chain(*ways['nodes']))
        nodes = nodes.loc[nodes['node_id'].isin(relevant_nodes)]

        return ways, nodes

    def _create_munich_streets(self):
        """
        Converts the osm_ways and osm_nodes to the format employed by the munich model
        to handle streets and intersections: street_k --> [intersection_n, intersection_m]
        :return: street dataframe in the correct format.
        """

        ways, _ = self._parse_to_df()

        street_df = pd.DataFrame()
        begin_inter, end_inter = [], []
        width, height, typo = [], [], []
        intensity, street_names = [], []

        for _, w in ways.iterrows():
            street_nodes = w['nodes']
            for i, node in enumerate(street_nodes[:-1]):
                begin_inter.append(node)
                end_inter.append(street_nodes[i+1])
                width.append(w['width'])
                height.append(w['height'])
                typo.append(w['typo'])
                intensity.append(w['intensity'])
                street_names.append(w['street_name'])

        street_df['street_id'] = range(1, len(end_inter) + 1)
        street_df['begin_inter'] = begin_inter
        street_df['end_inter'] = end_inter
        street_df['width'] = width
        street_df['height'] = height
        street_df['typo'] = typo
        street_df['intensity'] = intensity
        street_df['street_name'] = street_names

        self.street_df = street_df

    def _create_munich_intersections(self):
        """
        Converts the osm_ways and osm_nodes to the format employed by the munich model
        to handle streets and intersections: street_k --> [intersection_n, intersection_m]
        :return: intersection dataframe in the correct format.
        """

        _, self.intersection_df = self._parse_to_df()

        # Se encuentran todas las calles en las que aparece cada índice de intersección.
        self.intersection_df['streets'] = [findStreets(i, self.street_df) for i in self.intersection_df['node_id']]
        self.intersection_df['number_of_streets'] = [
            len(node_streets) for node_streets in self.intersection_df['streets']
        ]

    def _reset_intersection_ids(self):
        """
        Resets the ids of the intersections to id = id - min(ids)
        :return:
        """

        mapping = {
            original: new for new, original in
            enumerate(self.intersection_df['node_id'], start=1)
        }

        self.intersection_df['node_id'] = self.intersection_df['node_id'].map(mapping)
        self.street_df['begin_inter'] = self.street_df['begin_inter'].map(mapping)
        self.street_df['end_inter'] = self.street_df['end_inter'].map(mapping)

    def _add_street_length(self):
        """
        Añade una columna de longitud a self.street_df.
        :return:
        """

        lengths = []
        for _, street in self.street_df.iterrows():
            lat1, lon1 = self.intersection_df.loc[
                self.intersection_df['node_id'] == street['begin_inter'], ['lat', 'lon']
            ].values[0]

            lat2, lon2 = self.intersection_df.loc[
                self.intersection_df['node_id'] == street['end_inter'], ['lat', 'lon']
            ].values[0]

            lengths.append(haversine_distance([lat1, lon1], [lat2, lon2]))

        self.street_df['length'] = lengths
        self.street_df = self.street_df[
            ['street_id', 'begin_inter', 'end_inter', 'length', 'width', 'height', 'typo', 'intensity', 'street_name']
        ]

    def _find_nodes(self, *node_ids):
        """
        A partir de un node_id encuentra la correspondiente fila de intersection_df
        :param node_ids:
        :return:
        """
        return [self.intersection_df.loc[self.intersection_df['node_id'] == node_id] for node_id in node_ids]

    def _find_streets(self, *street_ids):
        """
        A partir de un street_id encuentra la correspondiente fila de street_df
        :param street_ids:
        :return:
        """
        return [self.street_df.loc[self.street_df['street_id'] == street_id] for street_id in street_ids]

    def _find_drop_node(self, begin_node, end_node, equals=0):
        """
        Encuentra cuál de los dos nodos suministrados se compone de menos calles. Si ambos tienen el mismo número,
        se suprime el primero por defecto.
        :param begin_node:
        :param end_node:
        :param equals: en caso de que ambos nodos se compongan del mismo número de calles, cuál de ellos eliminar.
        :return:
        """

        begin_length = len(begin_node['streets'])
        end_lengh = len(end_node['streets'])

        if begin_length == end_lengh:
            keep_node, drop_node = (end_node, begin_node) if equals == 0 else (end_node, begin_node)

        elif begin_length > end_lengh:
            keep_node, drop_node = begin_node, end_node

        else:
            keep_node, drop_node = end_node, begin_node

        return keep_node, drop_node

    def _adjust_nodes(self, street_id, adj_begin, adj_end, keep_node, drop_node):
        """
        Dados los begin_inter y end_inter de una calle que formaba parte de un nodo que se
        va a eliminar, encuentra dicho nodo y lo sustituye por el nuevo.
        :param adj_begin:
        :param adj_end:
        :param keep_node:
        :param drop_node:
        :return:
        """

        if adj_begin == drop_node:
            self.street_df.loc[
                self.street_df['street_id'] == street_id, 'begin_inter'
            ] = keep_node

        elif adj_end == drop_node:
            self.street_df.loc[
                self.street_df['street_id'] == street_id, 'end_inter'
            ] = keep_node

        else:
            print(
                f'WARNING: Any of the nodes [{adj_begin}, {adj_end}] of street {street_id} '
                f'correspond to the node {drop_node} being removed.'
            )

    def _clear_droped_street(self, keep_node_id, drop_node_id, drop_street):
        """
        Elimina la calle drop_street de la lista de calles de node_id
        :param keep_node_id:
        :param drop_node_id:
        :param drop_street:
        :return:
        """

        keep_node_streets = self.intersection_df.loc[
            self.intersection_df['node_id'] == keep_node_id, 'streets'
        ]

        drop_node_streets = self.intersection_df.loc[
            self.intersection_df['node_id'] == drop_node_id, 'streets'
        ]

        new_keep_node_streets = [
            street for street in keep_node_streets.iloc[0]+drop_node_streets.iloc[0]
            if street != drop_street
        ]

        self.intersection_df.loc[
            self.intersection_df['node_id'] == keep_node_id, 'streets'
        ] = pd.Series(
            [new_keep_node_streets],
            index=keep_node_streets.index
        )

    def _drop_short_streets(self, short_streets):
        """
        Elimina las calles cortas de self.street_df
        :param short_streets:
        :return:
        """

        self.street_df.drop(short_streets.index, inplace=True)

    def _drop_unused_nodes(self):
        """
        Elimina las intersecciones no usadas en self.street_df
        :return:
        """

        used_nodes = self.street_df['begin_inter'].unique().tolist() + self.street_df['end_inter'].unique().tolist()

        self.intersection_df = self.intersection_df.loc[
            self.intersection_df['node_id'].isin(used_nodes)
        ]

    def _merge_streets(self, min_length=10.0):
        """
        Cuando se encuentra una calle cuya longitud es menor que "min_length", esta se sustituye por
        una intersección.
        """

        # 1. Identificar qué calles se van a mergear
        short_streets = self.street_df.loc[
            self.street_df['length'] < min_length, ['street_id', 'begin_inter', 'end_inter']
        ]

        for _, short in short_streets.iterrows():
            # 2. Encontrar cuál de las dos intersecciones se suprime: la que menos calles tenga
            begin_node, end_node = self._find_nodes(short['begin_inter'], short['end_inter'])
            keep_node, drop_node = self._find_drop_node(begin_node, end_node)

            # 3. Modificar las calles que estaban conectadas al drop_node para que
            # se conecten al keep_node.
            for adjacent_street in drop_node['streets'].iloc[0]:
                adjacent_begin_node, adjacent_end_node = self._find_streets(
                    adjacent_street
                )[0][['begin_inter', 'end_inter']].iloc[0]

                self._adjust_nodes(
                    adjacent_street, adjacent_begin_node, adjacent_end_node,
                    keep_node['node_id'].iloc[0], drop_node['node_id'].iloc[0]
                )

            # 4. Eliminar la calle que se está mergeando de la lista de calles del keep_node.
            self._clear_droped_street(
                keep_node['node_id'].iloc[0],
                drop_node['node_id'].iloc[0],
                short['street_id']
            )

        # 5. Eliminar las calles cortas y quedarse solo con las intersecciones que se usan
        self._drop_short_streets(short_streets)
        self._drop_unused_nodes()

    def _writeIntersections(self):
        """
        Writes the intersections to file.
        :return:
        """

        filepath = os.path.join(config.LEZ_DIR, f'{self.city}/domain/intersection.dat')

        with open(filepath, "w") as f:
            f.write("#id;lon;lat;number_of_streets;1st_street_id;2nd_street_id;..." + "\n")

            for _, intersection in self.intersection_df.iterrows():
                f.write(
                    f"{int(intersection['node_id'])};{intersection['lon']};" +
                    f"{intersection['lat']};{intersection['number_of_streets']};" +
                    ";".join(map(str, intersection['streets'])) + "; \n"
                )


if __name__ == "__main__":
    from munpy.general import dat_to_geojson

    # Test polygon download
    with open('/home/ngomariz/test_polygon.geojson', 'r') as ff:  # Un polígono cualquiera en geoJSON
        gjs = json.load(ff)

    coords = gjs['features'][0]['geometry']['coordinates'][0]
    get_gounding_polygon(
        name='test_area', coordinates=coords, savepath=os.path.join(config.LEZ_DIR, 'test/domain/map.osm')
    )

    # Create MUNICH files once the OSM data is downloaded
    osm = OSMHandler('test')
    streets, intersections = osm.create_munich_files(save=False)

    # Get a geoJSON file with the street profiles
    street_gjs = dat_to_geojson(streets, intersections)
    with open(os.path.join(config.LEZ_DIR, 'test/domain/street.geojson'), 'w') as gjs:
        json.dump(street_gjs, gjs)
