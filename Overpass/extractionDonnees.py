# -*- coding: utf-8 -*-

import overpy
import streamlit as st
    
def loadDatas(data, node = True):
    if node:
        lat = data.lat
        lon = data.lon
    else:
        if isinstance(data, overpy.Way):
            lats, lons = [], []
            for node in data.nodes:
                lats.append(node.lat)
                lons.append(node.lon)
            lat = sum(lats) / len(lats)
            lon = sum(lons) / len(lons)
        
        # Pour les 'relations', on fait de même en prenant les nœuds des membres
        elif isinstance(data, overpy.Relation):
            lats, lons = [], []
            for member in data.members:
                if isinstance(member, overpy.Node):
                    lats.append(member.lat)
                    lons.append(member.lon)
            lat = sum(lats) / len(lats)
            lon = sum(lons) / len(lons)
    amenity = data.tags.get("amenity")
    shop = data.tags.get("shop")
    return {"id": data.id, "name": data.tags.get("name", "Nom inconnu"),    
            "amenity": amenity,
            "shop" : shop
            }, (lat,lon)
    
    
