from Malt.Render.Lighting import LightsBuffer, ShadowMaps

from Malt.GL import *
from Malt.UBO import UBO
from Malt.Texture import TextureArray, CubeMapArray
from Malt.RenderTarget import ArrayLayerTarget, RenderTarget
from Malt.Render import Common

from Malt import Pipeline

_SHADOWMAPS = None

def get_shadow_maps():
    if Pipeline.MAIN_CONTEXT:
        global _SHADOWMAPS
        if _SHADOWMAPS is None: _SHADOWMAPS = (NPR_ShadowMaps(), NPR_TransparentShadowMaps())
        return _SHADOWMAPS
    else:
        return (NPR_ShadowMaps(), NPR_TransparentShadowMaps())

class NPR_ShadowMaps(ShadowMaps):

    def __init__(self):
        super().__init__()
        self.spot_id_t = None
        self.sun_id_t = None
        self.point_id_t = None
    
    def setup(self, create_fbos=True):
        super().setup(False)
        self.spot_id_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_R32F)
        self.sun_id_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns * self.sun_cascades, GL_R32F)
        self.point_id_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_R32F)
        
        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                self.spot_fbos.append(RenderTarget([ArrayLayerTarget(self.spot_id_t, i)], ArrayLayerTarget(self.spot_depth_t, i)))

            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                self.sun_fbos.append(RenderTarget([ArrayLayerTarget(self.sun_id_t, i)], ArrayLayerTarget(self.sun_depth_t, i)))
            
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                self.point_fbos.append(RenderTarget([ArrayLayerTarget(self.point_id_t, i)], ArrayLayerTarget(self.point_depth_t, i)))
    
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear([0], depth=1)
        for i in range(sun_count * self.sun_cascades):
            self.sun_fbos[i].clear([0], depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear([0], depth=1)
    
    def shader_callback(self, shader):
        super().shader_callback(shader)
        shader.textures['SHADOWMAPS_ID_SPOT'] = self.spot_id_t
        shader.textures['SHADOWMAPS_ID_SUN'] = self.sun_id_t
        shader.textures['SHADOWMAPS_ID_POINT'] = self.point_id_t

class NPR_TransparentShadowMaps(NPR_ShadowMaps):

    def __init__(self):
        super().__init__()
        self.spot_color_t = None
        self.sun_color_t = None
        self.point_color_t = None
    
    def setup(self, create_fbos=True):
        super().setup(False)
        self.spot_color_t = TextureArray((self.spot_resolution, self.spot_resolution), self.max_spots, GL_RGBA32F)
        self.sun_color_t = TextureArray((self.sun_resolution, self.sun_resolution), self.max_suns * self.sun_cascades, GL_RGBA32F)
        self.point_color_t = CubeMapArray((self.point_resolution, self.point_resolution), self.max_points, GL_RGBA32F)
        
        if create_fbos:
            self.spot_fbos = []
            for i in range(self.spot_depth_t.length):
                targets = [ArrayLayerTarget(self.spot_id_t, i), ArrayLayerTarget(self.spot_color_t, i)]
                self.spot_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.spot_depth_t, i)))

            self.sun_fbos = []
            for i in range(self.sun_depth_t.length):
                targets = [ArrayLayerTarget(self.sun_id_t, i), ArrayLayerTarget(self.sun_color_t, i)]
                self.sun_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.sun_depth_t, i)))
            
            self.point_fbos = []
            for i in range(self.point_depth_t.length*6):
                targets = [ArrayLayerTarget(self.point_id_t, i), ArrayLayerTarget(self.point_color_t, i)]
                self.point_fbos.append(RenderTarget(targets, ArrayLayerTarget(self.point_depth_t, i)))
    
    def clear(self, spot_count, sun_count, point_count):
        for i in range(spot_count):
            self.spot_fbos[i].clear([0, (0,0,0,0)], depth=1)
        for i in range(sun_count * self.sun_cascades):
            self.sun_fbos[i].clear([0, (0,0,0,0)], depth=1)
        for i in range(point_count*6):
            self.point_fbos[i].clear([0, (0,0,0,0)], depth=1)

    def shader_callback(self, shader):
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_SPOT'] = self.spot_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_SUN'] = self.sun_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_DEPTH_POINT'] = self.point_depth_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_SPOT'] = self.spot_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_SUN'] = self.sun_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_ID_POINT'] = self.point_id_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_SPOT'] = self.spot_color_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_SUN'] = self.sun_color_t
        shader.textures['TRANSPARENT_SHADOWMAPS_COLOR_POINT'] = self.point_color_t
        

