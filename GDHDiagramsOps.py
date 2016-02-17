import requests, json, GeodesignHub
import shapelyHelper, diagramsJoin

import logging
from shapely.geometry.base import BaseGeometry
from shapely.geometry import shape, mapping, shape, asShape
from shapely.geometry import MultiPolygon, MultiPoint, MultiLineString
from shapely import speedups
import shapelyHelper
from shapely.ops import cascaded_union

import geobuf
from io import BytesIO
class DiagramCombiner():
	''' A class to conduct basic (6) GIS operations during copy diagrams. '''

	def genFeature(self, geom, allGeoms, errorCounter):
		try:
			curShape = asShape(geom)
			allGeoms.append(curShape)
		except Exception as e:
			logging.error(explain_validity(curShape))
			errorCounter+=1
		return allGeoms, errorCounter

	def combineDiagrams(self, shapesList):
		combinedGeoms = []
		cf ={}
		finalPolygons = cascaded_union(shapesList)
		j = json.loads(shapelyHelper.export_to_JSON(finalPolygons))
		cf['type']= 'Feature'
		cf['properties']= {}
		cf['geometry']= j
		combinedGeoms.append(cf)
		return combinedGeoms		

	def processGeoms(self, firstDiagram, secondDiagram, mode):

		if (mode == 'combine'):
			firstGeoms =[]
			secondGeoms =[]
			for curFeature in firstDiagram['features']:
				firstGeoms, errorCounter = self.genFeature(curFeature['geometry'],allGeoms=firstGeoms, errorCounter=0)

			for curFeature in secondDiagram['features']:
				secondGeoms, errorCounter = self.genFeature(curFeature['geometry'],allGeoms=secondGeoms, errorCounter=0)

			combinedGeoms = firstGeoms + secondGeoms
			newGeoms = self.combineDiagrams(combinedGeoms)

		elif (mode =='stitch'):
			newGeoms = []
			for curFeature in firstDiagram['features']:
				curFeature['properties'] = {}
				newGeoms.append(curFeature)
			for curFeature in secondDiagram['features']:
				curFeature['properties'] = {}
				newGeoms.append(curFeature)


		transformedGeoms = {}
		transformedGeoms['type'] = 'FeatureCollection'
		transformedGeoms['features'] = newGeoms

		return transformedGeoms


if __name__ == "__main__":
	firstAPIHelper = GeodesignHub.GeodesignHubClient(url = 'https://www.geodesignhub.com/api/v1/', project_id='d962fdcb18d9334ac2', token='d75393abe78ae71c87750ef71c2ac0bf2afeb093')

	firstDiagID = 32 # diagram to be downloaded
	r1 = firstAPIHelper.get_diagram_geoms(firstDiagID)

	secondAPIHelper = GeodesignHub.GeodesignHubClient(url = 'https://www.geodesignhub.com/api/v1/', project_id='d962fdcb18d2394ac2', token='d75393abe78ae71c87750ef71c2ac0bf2afeb093')

	secondDiagID = 32 # diagram to be downloaded
	r2 = secondAPIHelper.get_diagram_geoms(secondDiagID)

	if r1.status_code == 200:
		op = json.loads(r1.text)
		firstgeoms = op['geojson']

	if r2.status_code == 200:
		op = json.loads(r2.text)
		secondgeoms = op['geojson']

	myDiagramCombiner = self.DiagramCombiner()
	combinedGJ = myDiagramCombiner.processGeoms(firstgeoms, secondgeoms, 'stitch')

	print combinedGJ

	targetReqID= 12
	upload = myAPIHelper.post_as_diagram(geoms = combinedGJ, projectorpolicy= 'project',featuretype = 'polygon', description= 'Original Corridoor', reqid = targetReqID)
	print upload.text