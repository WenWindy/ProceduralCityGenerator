'''
Environment Generator Project
Script by Windy Wen
Aug 14th, 2021
With assistance from BCIT
'''

#Add dependencies
import maya.cmds as cmds
import random
from random import uniform as rand
import time
import os
import maya.mel as mel

# create UI class
class UI(object):
       
    def __init__(self):    
        # define variables 
        cmds.select(cl=True)
        # terrain
        self.DimVal=20
        self.DivVal=20
        self.HeightVal=1.0
        self.DepthVal=-1.0
        # building
        self.copiesBuilding = 10
        self.offsetValBuilding = 0
        self.randRotateBuilding = 0
        self.rotAlongCRVBuilding = False
        self.randScaleBuilding = 0.0
        self.buildingCondition = False
        self.buildingCRVCondition = False
        # curve
        self.widthValRoad = 1
        self.divValRoad = 15
        self.heightValRoad = 0
        self.riverValRoad = False
        self.usePlane = True
        self.userRoadCopy = 10
        self.populateRoadMesh = 0
        # light
        self.userNorth = 0
        self.userTime = 0
        self.userWeather = 0
        self.dynamicScene = False
        self.userFrameStart = 0
        self.userFrameEnd = 200
        self.userTimeStart = 6
        self.userTimeEnd = 18
        self.changeIntensity = 1.0
        self.userLightColor = (1.0, 1.0, 1.0)
        self.userWeatherTerrain = None

    # make UI window
    def makeUI(self):
        # check if window exists
        if cmds.window("envGenerator", q = True, ex = True):
            cmds.deleteUI("envGenerator")
        # create window
        cmds.window("envGenerator", title = 'Environment Generator', 
                    sizeable = False, width = 500, height = 800)
        # create UI layout
        self.layoutUI()
        # display window
        cmds.showWindow()

    # make window UI layout
    def layoutUI(self):
        # create tabs
        cmds.tabLayout("mainTab", scrollable = True, 
                        innerMarginHeight = 5, innerMarginWidth = 5)
        
    ######################
    ### Tab 1: Terrain ###
    ######################
        
        # create terrain tab
        cmds.columnLayout("terrainLayout")
        cmds.tabLayout("mainTab", edit = True, 
                        tabLabel = ["terrainLayout", "Terrain"])
        
        
    ### 1. choose terrain mesh ###
        cmds.frameLayout("terrainMesh", label = "Create or upload terrain", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # check if want to use own mesh
        cmds.text("You can import terrain from your computer if needed.")
        # user import mesh 
        cmds.button(label = "import terrain", width = 100, command = self.importMesh)
        
        # go back to terrain tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("terrainLayout")
        
    ### 2. create terrain ###
        cmds.frameLayout("createTerrain", label = "Terrain Creation", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # get parameters
        cmds.text("Please modify parameters for the terrain")
        self.PlaneDim=cmds.intSliderGrp(l="Dimension:",f=True,min=10,max=50,v=20,cc=self.getDim)
        self.PlaneDiv=cmds.intSliderGrp(l="Division:",f=True,min=10,max=50,v=20,cc=self.getDiv)
        self.MaxHeight=cmds.floatSliderGrp(l="Maximun Height:",f=True,min=0.0,max=5.0,v=0.5,cc=self.getHei)
        self.MaxDepth=cmds.floatSliderGrp(l="Maximun Depth:",f=True,min=-5.0,max=0.0,v=-0.5,cc=self.getDep)
        cmds.button(l="Create",backgroundColor = (0, 0.5, 0.3),command=self.CreateTerrain)
        self.terrainU=cmds.button(l="Undo",bgc = (0.5, 0.2, 0.2),command=self.UndoTerrain, enable=False)
        
    ### 3. apply texture ###
        cmds.frameLayout("terrainShader", label = "Apply terrain texture", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False, enable =True)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # user import road texture
        cmds.text("You can import texture from your computer if needed.")
        self.terrainTexture = cmds.button(label = "Import texture", width = 100, enable = False,
                                        command = self.importTerrainImage)
        
        self.undoTerrainTexture = cmds.button(label = "Undo Shader", width = 100, enable = False,
                                        command = self.delTerrainImage)
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("terrainLayout")
        
        ## go back to main tab
        cmds.setParent("mainTab")

        
    #######################
    ### Tab 2: Building ###
    #######################
        
        # create Building tab
        cmds.columnLayout("buildingLayout", columnAlign = "left")
        cmds.tabLayout("mainTab", edit = True, 
                        tabLabel = ["buildingLayout", "Building / Tree "])
        
    ### 1. choose building mesh ###
        cmds.frameLayout("buildingMesh", label = "Import and select mesh", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        cmds.text("You can import mesh from your computer if needed.")
        # user import mesh 
        cmds.button(label = "import mesh", width = 100, command = self.importMesh)
        # user choose mesh
        cmds.text(label = "Add/remove objects to the list:")
        cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1,90),(2,90)])
        # buttons
        cmds.button(label = "add", command = self.addBuilding)
        cmds.button(label = "remove", command = self.remBuilding)
        cmds.setParent("..")
        cmds.columnLayout(columnAlign = "center")
        # text scrollist to contain selected obj
        self.selectedBuilding = cmds.textScrollList(allowMultiSelection = True, 
                                                    selectCommand = self.selectBuilding)
        
        # go back to building tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("buildingLayout")
        
           
    ### 2. choose curve ###
        cmds.frameLayout("buildingCurve", label = "Select the curve you want to build on", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        self.selectedBuildingCurve = cmds.textFieldButtonGrp(label = "Select the curve: ", 
                                                            buttonLabel = "Select", editable = False,
                                                            buttonCommand=self.selectBuildingCRV)    

        # go back to building tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("buildingLayout")
                
        
    ### 3. populating paramerters ###
        cmds.frameLayout("buildingParam", label = "Modify populating parameters if needed", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # number of copies
        self.copyBuilding = cmds.intSliderGrp(  label = "Number of copies: ", 
                                                value = 10, field = True, min = 3, max = 100,
                                                changeCommand = self.buildingCP)
        # position offset
        self.offsetBuilding = cmds.intSliderGrp(label = "Position offset: ", 
                                                value = 0, field = True, min = -50, max = 50, 
                                                changeCommand = self.buildingPO)        
        # random rotation
        self.rotationBuilding = cmds.intSliderGrp(  label = "random rotation: ", 
                                                    value = 0, field = True, min = -180, max = 180, 
                                                    changeCommand = self.buildingRR)
        # rotate along curve
        self.curveRotation = cmds.checkBox( label = "Rotate along curve", value = False, align = "center",
                                            changeCommand = self.buildingCR)                                            
        # random size
        self.sizeBuilding = cmds.floatSliderGrp(label = "size randomness: ", 
                                                value = 0, f = True, min = 0, max = 10, 
                                                changeCommand = self.buildingRS)    
        
        # go back to building tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("buildingLayout")
        
        
    ### 4. populate ###
        cmds.frameLayout("buildingPopulate", label = "Populating", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        self.populate = cmds.button(label = "Populate", backgroundColor = (0, 0.5, 0.3), 
                                    command = self.makeBuilding, enable = False)
        self.undoBuilding = cmds.button(label = "Undo", backgroundColor = (0.5, 0.2, 0.2), 
                                        command = self.deleteBuilding, enable = False)

        # go back to building tab
        cmds.setParent("buildingLayout")
        
        ### go back to main tab
        cmds.setParent("mainTab")
        
        
    #########################        
    ### Tab 3: Road/River ###
    #########################
        
        # create Road/River tab
        cmds.columnLayout("roadLayout")
        cmds.tabLayout("mainTab", edit = True, 
                        tabLabel = ["roadLayout", "Road/River"])
        
    ### 1. choose curve ###
        cmds.frameLayout("roadCurve", label = "Select the curve you want to build along", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        self.selectedRoadCurve = cmds.textFieldButtonGrp(label = "Select the curve: ", 
                                                            buttonLabel = "Select", editable = False,
                                                            buttonCommand=self.selectRoadCRV)    

        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("roadLayout")   

    ### 2. road style ###
        cmds.frameLayout("roadStyle", label = "Road / River parameters", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)    
        
        ## content
        # default road or user import road mesh
        cmds.text("You can create default road or upload your own.")
        cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1,250),(2,250)])
        # ask if want default or own road
        self.importRoad = cmds.button(label = "Import road/river mesh", width = 100, command = self.importMesh, enable = False)
        self.defaultRoad = cmds.checkBox(label = "Use default road", value = True, align = "right", changeCommand = self.default)
        cmds.setParent("..")
        cmds.columnLayout(columnAlign = 'center')
        # select user road
        self.userRoad = cmds.textFieldButtonGrp(label = "Select your mesh: ", enable = False,
                                                buttonLabel = "Select", editable = False,
                                                buttonCommand=self.selectUserRoad)
        # road copies
        self.copyRoad = cmds.intSliderGrp(  label = "Number of copies: ", enable =False,
                                            value = 10, field = True, min = 1, max = 100,
                                            changeCommand = self.roadC)
        cmds.separator(style="none", height=3)
        
    ### 2.1 default road parameter ###
        cmds.frameLayout("roadParam", label = "Default road parameters", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)    
        
        # road width
        self.widthRoad = cmds.floatSliderGrp(label = "Road Width: ", 
                                            value = 1, field = True, min = 0.1, max = 10,
                                            changeCommand = self.roadW)
        # road division
        self.divisionRoad = cmds.intSliderGrp(label = "Road division: ", 
                                                value = 10, field = True, min = 1, max = 500, 
                                                changeCommand = self.roadD)        
        # height offset
        self.heightRoad = cmds.floatSliderGrp(  label = "Height offset: ", 
                                                value = 0, field = True, min = -10, max = 20, 
                                                changeCommand = self.roadH)
        # make river
        self.river = cmds.checkBox( label = "Make river ", value = False, align = "center",
                                    changeCommand = self.roadR)       
        # go back to main parameter tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("roadStyle")
        
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("roadLayout")        
        
        
    ### 3. make road ###
        cmds.frameLayout("roadPopulate", label = "Make road or river", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        self.makeRoad = cmds.button(label = "Make", backgroundColor = (0, 0.5, 0.3), 
                                    command = self.makingRoad, enable = False)
        self.undoRoad = cmds.button(label = "Undo", backgroundColor = (0.5, 0.2, 0.2), 
                                        command = self.deleteRoad, enable = False)
        
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("roadLayout")
    
    
    ### 4. apply texture ###
        cmds.frameLayout("roadShader", label = "Apply road texture", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False, enable =True)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # user import road texture
        cmds.text("You can import texture from your computer if needed.")
        self.roadTexture = cmds.button(label = "Import texture", width = 100, enable = False,
                                        command = self.importRoadImage)
        
        self.undoRoadTexture = cmds.button(label = "Undo Shader", width = 100, enable = False,
                                        command = self.delRoadImage)
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("roadLayout")
        
        
        ## go back to main tab
        cmds.setParent("mainTab")

        
    #######################
    ### Tab 4: Lighting ###
    #######################
        
        # create Extra tab
        cmds.columnLayout("lightLayout")
        cmds.tabLayout("mainTab", edit = True, 
                        tabLabel = ["lightLayout", "Lighting"])
    
    ### 1. choose time ###
        cmds.frameLayout("lightTime", label = "Choose the time of the day you want for the scene", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        
        # choosing the north direction
        cmds.text("Please choose your north direction:")
        self.getNorth = cmds.radioButtonGrp(adjustableColumn4 = 4, numberOfRadioButtons=4,
                            labelArray4= ("x", "-x", "z", "-z"), changeCommand=self.north)
        # choosing the time of the day
        cmds.text("Please choose your time of the day: ")
        self.getTime = cmds.intSliderGrp(label="Time of the Day (hour): ", max=23, min=0, field=True,
                                        value = 0, changeCommand = self.time)
        self.userDynamic = cmds.checkBox(label="Dynamic Scene", value = False, changeCommand = self.dynamic)
        
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("lightLayout")            

    ### 2. light settings
        cmds.frameLayout("lightSetting", label = "Customize your lighting", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # choose the intensity
        self.lightInt=cmds.floatSliderGrp(label="Light Intensity: ", max=10, min=0.1, field=True, 
                                        value=1, changeCommand = self.lightIntensity)
        # choosing the color
        self.getLightColor = cmds.colorInputWidgetGrp(label="Light Color: ", changeCommand = self.lightColor)
                
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("lightLayout")           

    ### 3. weather
        cmds.frameLayout("lightWeather", label = "Choose your dynamic scene preset", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False, enable=False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        # choosing end frame
        cmds.text("Please choose your frame range of the animation:")
        self.getStartFrame = cmds.intSliderGrp(label="Start frame: ", min=0, max = 10000, field=True,
                                                value = 0, changeCommand = self.userFrame)
        self.getEndFrame = cmds.intSliderGrp(label="End frame: ", min=1, max = 10000, field=True,
                                                value = 200, changeCommand = self.userFrame)
        # choosing time range
        cmds.text("Please choose your time range of the day: ")
        self.getStartTime = cmds.intSliderGrp(label="Start time (hour): ", max=23, min=0, field=True,
                                            value = 6, changeCommand = self.timeRange)
        self.getEndTime = cmds.intSliderGrp(label="End time (hour): ", max=23, min=0, field=True,
                                            value = 18, changeCommand = self.timeRange)
        # choosing weather
        cmds.text("Please choose the weather of your scene:")
        self.getWeather = cmds.radioButtonGrp(adjustableColumn4 = 4, numberOfRadioButtons=4,
                            labelArray4= ("Sunny", "Cloudly", "Rainy", "Snowy"), changeCommand=self.weather)
        self.getWeatherTerrain = cmds.textFieldButtonGrp(label = "Select the terrain: ", 
                                                        buttonLabel = "Select", editable = False,
                                                        buttonCommand=self.weatherTerrain)
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("lightLayout")
      
    ### 4. create
        cmds.frameLayout("createLight", label = "Create your lighting", width = 500,
                            marginWidth = 5, collapsable = True, collapse = False)
        cmds.separator(style = "none", height = 3)
        
        ## content
        self.createLight = cmds.button(label = "Create", backgroundColor = (0, 0.5, 0.3), 
                                    command = self.makingLight, enable = False)
        self.undoLight = cmds.button(label = "Undo", backgroundColor = (0.5, 0.2, 0.2), 
                                        command = self.deleteLight, enable = False)
        
        # go back to road tab
        cmds.separator(style = "none", height = 3)
        cmds.setParent("lightLayout")
        
        
        ## go back to main tab
        cmds.setParent("mainTab")


##########################################
    # all UI functions begins here
##########################################    

######### general ###########

    def importMesh(self, *args):
        # load mesh from user computer
        meshFilter = "*.obj ;; *.fbx ;; *.abc"
        userMesh = cmds.fileDialog2(caption = "Choose the items you want to import", 
                        fileMode = 4, okCaption = "Import", fileFilter = meshFilter)
        for mesh in userMesh:
            # get file extension format
            fileExtension = os.path.splitext(mesh)
            # import obj
            if fileExtension[1] == ".obj":
                cmds.file(mesh, i = True, type = "OBJ", options = "mo=1", ignoreVersion = True, 
                            renameAll = True, preserveReferences = True, importTimeRange = "combine")
            # import fbx
            if fileExtension[1] == ".fbx":
                cmds.file(mesh, i = True, type = "FBX", options = "fbx", ignoreVersion = True, 
                            renameAll = True, preserveReferences = True, importTimeRange = "combine")
            # import abc
            if fileExtension[1] == ".abc":
                #cmds.AbcImport(mesh)
                cmds.file(mesh, i = True, type = "Alembic", ignoreVersion = True, 
                            renameAll = True, preserveReferences = True, importTimeRange = "combine")
            print "%s has imported."%mesh
    
######### 1. Terrain ###########

    # get parameters
    def getDim(self, *args):
        self.DimVal=cmds.intSliderGrp(self.PlaneDim,q=True,v=True)
        return self.DimVal
    def getDiv(self, *args):
        self.DivVal=cmds.intSliderGrp(self.PlaneDiv,q=True,v=True)
        return self.DivVal
    def getHei(self, *args):
        self.HeightVal=cmds.floatSliderGrp(self.MaxHeight,q=True,v=True)
        return self.HeightVal
    def getDep(self, *args):    
        self.DepthVal=cmds.floatSliderGrp(self.MaxDepth,q=True,v=True)
        
    def CreateTerrain(self, *args):
        # call class instances
        self.terrainClass = Terrain(self.DimVal, 
                                    self.DivVal, 
                                    self.HeightVal, 
                                    self.DepthVal)
        cmds.button(self.terrainU, edit=True, enable=True)
        cmds.button(self.terrainTexture, edit=True, enable=True)
        
    def UndoTerrain(self, *args):
        cmds.button(self.terrainU, edit=True, enable=False)
        cmds.button(self.terrainTexture, edit=True, enable=False)
        cmds.button(self.undoTerrainTexture, edit=True, enable=False)
        self.terrainClass.UndoTerrain()
        
    def importTerrainImage(self, *args):
        # call function in terrain class
        self.terrainClass.terrainShader()
        # enable button
        cmds.button(self.undoTerrainTexture, edit = True, enable = True)

    def delTerrainImage(self, *args):
        # enable button
        cmds.button(self.undoTerrainTexture, edit = True, enable = False)
        # call function in terrain class
        self.terrainClass.undoTexture()


######### 2. Building ###########
    def addBuilding(self, *args): 
        # get selected items
        selectedBuildingScene = cmds.ls(selection = True, objectsOnly = True)
        # adding selected scene obj to the list
        for i in selectedBuildingScene:
            cmds.textScrollList(self.selectedBuilding, edit = True, append = i)
            print 'Object' + i + ' has been added.'            
        cmds.select(cl = True)
        
    def remBuilding(self, *args):
        # remove the selected building
        selectedBuildingIndex = cmds.textScrollList(self.selectedBuilding, query= True, selectItem = 1)
        cmds.textScrollList(self.selectedBuilding, edit = True, removeItem = selectedBuildingIndex)
        
    def selectBuilding(self, *args):
        # select item from list for populate
        self.populateBuilding = cmds.textScrollList(self.selectedBuilding, query = True, selectItem = True)
        # check if user selected
        if self.populateBuilding:
            self.buildingCondition = True
        self.buildingPopulateCondition()
        return self.populateBuilding

    def selectBuildingCRV(self, *args):
        # select the curve user want to build on
        self.populateBuildingCRV = cmds.ls(selection = True, objectsOnly = True)
        cmds.textFieldButtonGrp(self.selectedBuildingCurve, edit = True, text = self.populateBuildingCRV[0])
        # check if user selected
        if self.populateBuildingCRV[0]:
            self.buildingCRVCondition = True
        return self.populateBuildingCRV[0]
    
    def buildingPopulateCondition(self, *args):
        # check if both building and curve selected, then enable "populate" button
        if (self.buildingCondition == True) and (self.buildingCRVCondition == True):
            print "The " + str(self.populateBuilding) + " is chosen for population."
            print "The " + str(self.populateBuildingCRV[0]) + " is chosen for path."
            cmds.button(self.populate, edit =True, enable = True)
        else:
            pass

    # change commands (get user inputs of: copies, position offset, rotation, random size)
    def buildingCP(self, *args):
        self.copiesBuilding = cmds.intSliderGrp(self.copyBuilding, query = True, value = True)
        return self.copiesBuilding
    
    def buildingPO(self, *args):
        self.offsetValBuilding = cmds.intSliderGrp(self.offsetBuilding, query = True, value = True)
        return self.offsetValBuilding
    
    def buildingRR(self, *args):
        self.randRotateBuilding = cmds.intSliderGrp(self.rotationBuilding, query = True, value = True)
        return self.randRotateBuilding
    
    def buildingCR(self, *args):
        self.rotAlongCRVBuilding = cmds.checkBox(self.curveRotation, query = True, value = True)
        # disable random rotation if rotate along curve
        if self.rotAlongCRVBuilding == True:
            cmds.intSliderGrp(self.rotationBuilding, edit = True, enable = False)
        if self.rotAlongCRVBuilding == False:
            cmds.intSliderGrp(self.rotationBuilding, edit = True, enable = True)
        return self.rotAlongCRVBuilding
    
    def buildingRS(self, *args):
        self.randScaleBuilding = cmds.floatSliderGrp(self.sizeBuilding, query = True, value = True)
        return self.randScaleBuilding
        
    #call building class functions
    def makeBuilding(self, *args):
        # call building class instance
        self.buildingClass = Building(  self.copiesBuilding, 
                                        self.offsetValBuilding, 
                                        self.randRotateBuilding,
                                        self.rotAlongCRVBuilding, 
                                        self.randScaleBuilding,
                                        self.populateBuilding,
                                        self.populateBuildingCRV[0])
        # enable "undo" button
        cmds.button(self.undoBuilding, edit = True, enable = True)
    
    def deleteBuilding(self, *args):
        # call undo function from class Building
        cmds.button(self.undoBuilding, edit = True, enable = False)
        self.buildingClass.undo()



############ 3. Road  ##############
    def selectRoadCRV(self, *args):
        # select the curve user want to build on
        self.populateRoadCRV = cmds.ls(selection = True, objectsOnly = True)
        cmds.textFieldButtonGrp(self.selectedRoadCurve, edit = True, text = self.populateRoadCRV[0])
        cmds.select(cl = True)
        if self.populateRoadCRV:
            cmds.button(self.makeRoad, edit = True, enable = True)
        return self.populateRoadCRV[0]
        
    def selectUserRoad(self, *args):
        # select the mesh user want to use
        self.populateRoadMesh = cmds.ls(selection = True)
        cmds.textFieldButtonGrp(self.userRoad, edit = True, text = self.populateRoadMesh[0])
        cmds.select(cl = True)
        return self.populateRoadMesh[0]
      
        
    # change commands
    def roadW(self, *args):
        self.widthValRoad = cmds.floatSliderGrp(self.widthRoad, query = True, value = True)
        return self.widthValRoad

    def roadD(self, *args):
        self.divValRoad = cmds.intSliderGrp(self.divisionRoad, query = True, value = True)
        return self.divValRoad

    def roadH(self, *args):
        self.heightValRoad = cmds.floatSliderGrp(self.heightRoad, query = True, value = True)
        return self.heightValRoad

    def roadR(self, *args):
        self.riverValRoad = cmds.checkBox(self.river, query = True, value = True)
        return self.riverValRoad
    
    def default(self, *args):
        self.usePlane = cmds.checkBox(self.defaultRoad, query = True, value = True)
        if self.usePlane == False:
            cmds.button(self.importRoad, edit = True, enable = True)
            cmds.intSliderGrp(self.copyRoad, edit = True, enable = True)
            cmds.textFieldButtonGrp(self.userRoad, edit =True, enable =True)
            cmds.frameLayout("roadParam", edit = True, enable = False)
        if self.usePlane == True:
            cmds.button(self.importRoad, edit = True, enable = False)
            cmds.intSliderGrp(self.copyRoad, edit = True, enable = False)            
            cmds.textFieldButtonGrp(self.userRoad, edit =True, enable =False)
            cmds.frameLayout("roadParam", edit = True, enable = True)
        return self.usePlane
    
    def roadC(self, *args):
        self.userRoadCopy = cmds.intSliderGrp(self.copyRoad, query = True, value = True)
        return self.userRoadCopy
    
    # calling road class instance
    def makingRoad(self, *args):
        # make instance
        self.roadClass = Road(  self.widthValRoad,
                                self.divValRoad,
                                self.heightValRoad,
                                self.riverValRoad,
                                self.userRoadCopy,
                                self.populateRoadCRV[0],
                                self.populateRoadMesh,
                                self.usePlane)
        # enable buttons
        cmds.button(self.undoRoad, edit = True, enable = True)
        if self.usePlane == True:
            cmds.button(self.roadTexture, edit = True, enable = True)
        
    def deleteRoad(self, *args):        
        # disable buttons
        cmds.button(self.undoRoad, edit = True, enable = False)
        cmds.button(self.roadTexture, edit = True, enable = False)
        # call function in road class
        self.roadClass.undo()
        
    def importRoadImage(self, *args):
        # call function in road class
        self.roadClass.roadRiverShader()
        # enable button
        cmds.button(self.undoRoadTexture, edit = True, enable = True)

    def delRoadImage(self, *args):
        # enable button
        cmds.button(self.undoRoadTexture, edit = True, enable = False)
        # call function in road class
        self.roadClass.undoTexture()
        
############### 4. Light #################
    
    def north(self, *args):
        # get user north
        self.userNorth=cmds.radioButtonGrp(self.getNorth, query=True, select=True)
        self.enableLight()
    
    def time(self, *args):
        # get user time
        self.userTime=cmds.intSliderGrp(self.getTime, query=True, value=True)
        return self.userTime
    
    def dynamic(self, *args):
        # check if the user wants dynamic weather
        self.dynamicScene = cmds.checkBox(self.userDynamic, query = True, value = True)
        if self.dynamicScene == False:
            cmds.intSliderGrp(self.getTime, edit = True, enable = True)            
            cmds.frameLayout("lightWeather", edit = True, enable = False)
        if self.dynamicScene == True:
            cmds.button(self.createLight, edit =True, enable = False)
            cmds.intSliderGrp(self.getTime, edit = True, enable = False)            
            cmds.frameLayout("lightWeather", edit = True, enable = True)
        return self.dynamicScene
    
    def userFrame(self, *args):
        # get user frame range
        self.userFrameStart = cmds.intSliderGrp(self.getStartFrame, query=True, value=True)
        self.userFrameEnd = cmds.intSliderGrp(self.getEndFrame, query=True, value=True)

    
    def timeRange(self, *args):
        # get user time range 
        self.userTimeStart = cmds.intSliderGrp(self.getStartTime, query=True, value=True)
        self.userTimeEnd = cmds.intSliderGrp(self.getEndTime, query=True, value=True)
    
    def weather(self, *args):
        # get user weather
        self.userWeather=cmds.radioButtonGrp(self.getWeather, query=True, select=True)
        self.enableLight()
    
    def weatherTerrain(self, *args):
        # get the terrain
        self.userWeatherTerrain = cmds.ls(selection = True, objectsOnly = True)[0]
        cmds.textFieldButtonGrp(self.getWeatherTerrain, edit=True, text=self.userWeatherTerrain)
        cmds.select(clear=True)
        self.enableLight()
    
    def enableLight(self, *args):
        # check if all default selected, then enable "create" button
        if self.dynamicScene == False:
            if not (self.userNorth == 0):
                cmds.button(self.createLight, edit =True, enable = True)
            else:
                pass
        if self.dynamicScene == True:
            if self.userWeatherTerrain:
                if not (self.userNorth == 0) and not (self.userWeather == 0):
                    cmds.button(self.createLight, edit =True, enable = True)
            else:
                pass
        
    def makingLight(self, *args):
        # call light class instance
        self.lightClass = Light( self.userNorth,
                                 self.userTime,
                                 self.userWeather,
                                 self.dynamicScene,
                                 self.userFrameStart,
                                 self.userFrameEnd,
                                 self.userTimeStart,
                                 self.userTimeEnd,
                                 self.changeIntensity,
                                 self.userLightColor,
                                 self.userWeatherTerrain)
        # edit buttons enable/disable
        cmds.button(self.createLight, edit =True, enable = False)
        cmds.button(self.undoLight, edit =True, enable = True)
    
    def deleteLight(self, *args):
        self.lightClass.undo()
        # edit buttons enable/disable
        cmds.button(self.createLight, edit =True, enable = True)
        cmds.button(self.undoLight, edit =True, enable = False)
    
    def lightIntensity(self, *args):
        self.changeIntensity = cmds.floatSliderGrp(self.lightInt, query =True, value=True)
        return self.changeIntensity
    
    def lightColor(self, *args):
        self.userLightColor = cmds.colorInputWidgetGrp(self.getLightColor, query=True, rgb=True)
        print self.userLightColor


############################################
### all sub-classes create below 
############################################

###################################### TERRAIN
class Terrain(UI):
    def __init__(self, DimVal, DivVal, HeightVal, DepthVal):
        # receiving output from UI class
        self.DimVal=DimVal
        self.DivVal=DivVal
        self.HeightVal=HeightVal
        self.DepthVal=DepthVal
        # execution of creation
        self.CreateTerrain()
    
    def CreateTerrain(self, *args):
        cmds.promptDialog(title = "Name your terrain", 
                            message = "Please name the terrain: ", 
                            text = "terrain", button = "Create")
        self.nameTR = cmds.promptDialog(query =  True, text = True)
        self.terrain=cmds.polyPlane(n=self.nameTR,w=self.DimVal,h=self.DimVal,sw=self.DivVal,sh=self.DivVal)
        #select vertex
        SelectedObject=cmds.ls(selection=True)
        AllVerts=cmds.ls(SelectedObject[0]+".vtx[*]",flatten=True)
        cmds.select(AllVerts)
        #soft select
        cmds.softSelect(sse=1,ssd=5.0,ssc='0,1,2,1,0,2',ssf=2)
        #morphing
        for i in range(0,len(AllVerts),5):
            cmds.select(cl=True)
            singleVert=AllVerts[i]
            cmds.select(singleVert)
            
            RandX=rand(-1.0,1.0)
            RandY=rand(self.DepthVal,self.HeightVal)
            RandZ=rand(-1.0,1.0)
            cmds.move(RandX,RandY,RandZ,r=True)
            
            #time.sleep(0.001)
            cmds.NextFrame()
        cmds.softSelect(sse=0)
        cmds.select(cl=True)
        #go to first frame
        cmds.currentTime(1)
        
    def UndoTerrain(self, *args):
        cmds.select(self.nameTR, replace=True)
        cmds.delete()
        
    def terrainShader(self, *args):
        # create a shader for road
        shaderBlinn = cmds.shadingNode("blinn", asShader = True, name = "terrainShaderBlinn")
        self.file_node = cmds.shadingNode("file", asTexture = True, name ="texture")
        # load image from user computer
        self.imageFilter = "*.jpg ;; *.jpeg ;; *.png ;; *.tif ;; *.tiff ;; *.eps ;; *.raw"
        self.texture = cmds.fileDialog2(caption = "Choose the items you want to import", 
                                          fileMode = 1, okCaption = "Import", fileFilter = self.imageFilter)
        file = (self.texture[0])
        # get the shading group
        shading_group = cmds.sets(renderable = True, noSurfaceShader = True, empty = True)
        # set attributes
        cmds.setAttr("%s.fileTextureName"%self.file_node, file, type = "string")
        cmds.connectAttr("%s.outColor"%shaderBlinn, "%s.surfaceShader"%shading_group)
        cmds.select(self.terrain, replace = True)
        cmds.sets(self.terrain, edit = True, forceElement = shading_group)
        # create doublesided shader
        # condition node
        self.conditionNode = cmds.shadingNode("condition", asUtility=True)
        cmds.connectAttr("%s.outColor"%self.file_node, "%s.colorIfFalse"%self.conditionNode, force=True)
        cmds.connectAttr("%s.outColor"%self.file_node,"%s.colorIfTrue"%self.conditionNode, force=True)
        cmds.connectAttr("%s.outColor"%self.conditionNode, "%s.color"%shaderBlinn)
        # self.samplerInfo node
        self.samplerInfo = cmds.shadingNode("samplerInfo", asUtility=True)
        cmds.connectAttr("%s.flippedNormal"%self.samplerInfo, "%s.firstTerm"%self.conditionNode)
        # unitize UV
        cmds.polyForceUV(self.terrain, unitize=True)
        
    def undoTexture(self, *args):
        cmds.select("terrainShaderBlinn", replace=True)
        cmds.select(self.file_node, add=True)
        cmds.select(self.conditionNode, add=True)
        cmds.select(self.samplerInfo, add=True)
        cmds.delete()
    
        
###################################### BUILDING
class Building(UI):
    def __init__(self, copies, offset, randRotate, curveRotate, randScale, building, curves):
        # receiving output from UI class
        self.copies = copies
        self.offset = offset
        self.randRotate = randRotate
        self.curveRotate = curveRotate
        self.randScale = randScale
        self.building = building
        self.curves = curves
        
        # determine the starting frame of the timeline
        self.minFrame = cmds.playbackOptions(query = True, min = True)
        
        # executing populate function
        self.populate()
        
    # populating the building blocks
    def populate(self, *args):    
        folder = cmds.promptDialog(  title = "Name your folder", 
                            message = "Please name the folder that holds all your building duplications: ", 
                            text = "buildingGrp", button = "Create")
        # create a dummy node to animate along the curve: anim -> constrain -> attach to motion path
        cmds.spaceLocator(name = "bLoc")
        # select the locator and curve
        cmds.select(self.curves, add = True)
        # create motion path
        cmds.pathAnimation( fractionMode = True, follow = True, followAxis = "x", upAxis = "y",
                            inverseFront = False, startTimeU = 0, endTimeU = self.copies)
        # change motion to linear
        cmds.selectKey("motionPath1_uValue")
        cmds.keyTangent(inTangentType = "linear", outTangentType = "linear")
        # create empty folder to hold all buildings created later
        self.folderName = cmds.promptDialog(query =  True, text = True)
        parentFolder = cmds.group(empty = True, name = self.folderName)
        # multiply the buildings
        for obj in range(int(self.minFrame), int(self.minFrame) + self.copies):
            # get attributes of the locator every frame
            cmds.currentTime(obj, edit = True)
            currentX = cmds.getAttr("bLoc.tx")
            currentY = cmds.getAttr("bLoc.ty")
            currentZ = cmds.getAttr("bLoc.tz")
            currentRotY = cmds.getAttr('bLoc.ry')
            
            # select the building that chosen for population
            cmds.select(random.choice(self.building), replace = True)
            
            # duplicate the building mesh and set the translation according to locator
            tempObj = cmds.duplicate()
            cmds.setAttr(tempObj[0] + ".tx", currentX)
            cmds.setAttr(tempObj[0] + ".ty", currentY)
            cmds.setAttr(tempObj[0] + ".tz", currentZ)
            
            # using the info from user to modify translation
            newRotation = random.uniform(-self.randRotate, self.randRotate)
            newOffsetX = random.uniform(0, self.offset)
            newScale = random.uniform(1, self.randScale)
            
            # apply these modifications
            # rotation: along curve / random
            if self.curveRotate == True:
                cmds.setAttr(tempObj[0] + ".ry", currentRotY)
            else:
                cmds.rotate(0, newRotation, 0, relative = True)
            # translation
            cmds.move(newOffsetX, 0, 0, relative = True)
            # scale
            if self.randScale > 0:
                # makes sure the size randomness only happens when user change the parameter
                cmds.scale(newScale, newScale, newScale, relative = True)
            
            # parent all buildings created to the folder
            cmds.parent(tempObj[0], self.folderName, relative = False)  # let user name it
        
        # delete the dummy node
        cmds.select("bLoc")
        cmds.delete()    
    
    def undo(self, *args):
        cmds.select(self.folderName)
        cmds.delete()



########################################################## ROAD
class Road(UI):
    def __init__(self, width, div, height, river, copy, curves, userRoad, default):
        # define variables
        self.width = width
        self.div = div
        self.height = height
        self.river = river
        self.copy = copy
        self.curves = curves
        self.userRoad = userRoad
        self.default = default

        # check if user wants to use own model
        if self.default == True:
            # make road from scratch
            self.makeDefaultRoad()
        else:
            # populate user road
            self.makeUserRoad()
        
    def makeDefaultRoad(self, *args):
        # create base plane
        self.roadBase = cmds.polyPlane(n="roadBase", subdivisionsHeight = 1, subdivisionsWidth = 1, width = self.width)[0]
        cmds.select(self.curves, add=True)
        # create motion path
        cmds.currentTime(0, edit = True)
        cmds.pathAnimation( fractionMode = True, follow = True,
                            followAxis = "z", upAxis = "y",
                            inverseUp = False, inverseFront = False,
                            startTimeU = 1, endTimeU = 2)
        # extrude plane edge
        theRoad = cmds.polyExtrudeEdge("%s.e[0]"%self.roadBase, inputCurve = self.curves, divisions = self.div)
        cmds.select(self.roadBase, replace = True)    
        cmds.DeleteMotionPaths()
        # move road if user input height
        if self.height > 0:
            cmds.move(0, self.height, 0, relative = True)
        # make river if user checked
        if self.river:
            self.flattenRoad()
            
    def flattenRoad(self, *args):
        # make the road flat
        cmds.select(self.roadBase, replace = True)
        cmds.ConvertSelectionToVertices()
        cmds.scale(1,0,1, relative = True)        
    
    def roadRiverShader(self):
        if self.default == True:
            if self.river:
                # create river shader
                self.oceanShader = cmds.shadingNode("oceanShader", asShader=True)
                cmds.select(self.roadBase, replace=True)
                cmds.defaultNavigation(source=self.oceanShader, 
                                        destination="|%s|%sShape.instObjGroups[0]"%(self.roadBase,self.roadBase), 
                                        connectToExisting=True)

            else:
                # create a shader for the river/road
                shaderBlinn = cmds.shadingNode("blinn", asShader = True, name = "RoadShaderBlinn")
                self.file_node = cmds.shadingNode("file", asTexture = True, name ="texture")
                # load image from user computer
                self.imageFilter = "*.jpg ;; *.jpeg ;; *.png ;; *.tif ;; *.tiff ;; *.eps ;; *.raw"
                self.texture = cmds.fileDialog2(caption = "Choose the items you want to import", 
                                                  fileMode = 1, okCaption = "Import", fileFilter = self.imageFilter)
                print self.texture[0]
                file = (self.texture[0])
                # get the shading group
                shading_group = cmds.sets(renderable = True, noSurfaceShader = True, empty = True)
                # set attributes
                cmds.setAttr("%s.fileTextureName"%self.file_node, file, type = "string")
                cmds.connectAttr("%s.outColor"%shaderBlinn, "%s.surfaceShader"%shading_group)
                cmds.select(self.roadBase, replace = True)
                cmds.sets(self.roadBase, edit = True, forceElement = shading_group)
                # create doublesided shader
                # condition node
                self.conditionNode = cmds.shadingNode("condition", asUtility=True)
                cmds.connectAttr("%s.outColor"%self.file_node, "%s.colorIfFalse"%self.conditionNode, force=True)
                cmds.connectAttr("%s.outColor"%self.file_node,"%s.colorIfTrue"%self.conditionNode, force=True)
                cmds.connectAttr("%s.outColor"%self.conditionNode, "%s.color"%shaderBlinn)
                # self.samplerInfo node
                self.samplerInfo = cmds.shadingNode("samplerInfo", asUtility=True)
                cmds.connectAttr("%s.flippedNormal"%self.samplerInfo, "%s.firstTerm"%self.conditionNode)
                # unitize UV
                cmds.polyForceUV(self.roadBase, unitize=True)
        else:
            pass
        

    def undoTexture(self, *args):
        if self.river:
            cmds.select(self.oceanShader, replace=True)
            cmds.delete()
        else:
            cmds.select("RoadShaderBlinn", replace=True)
            cmds.select(self.file_node, add=True)
            cmds.select(self.conditionNode, add=True)
            cmds.select(self.samplerInfo, add=True)
            cmds.delete()
    
        
    def makeUserRoad(self, *args):
        # ask user to give a name for mesh duplicates
        folder = cmds.promptDialog(  title = "Name your folder", 
                            message = "Please name the folder that holds all your model duplications: ", 
                            text = "%sGrp"%self.userRoad , button = "Create")
        # create a dummy node to animate along the curve: anim -> constrain -> attach to motion path
        cmds.spaceLocator(name = "rLoc")
        # select the locator and curve
        cmds.select(self.curves, add = True)
        # create motion path
        cmds.pathAnimation( fractionMode = True, follow = True, followAxis = "x", upAxis = "y",
                            inverseFront = False, startTimeU = 0, endTimeU = self.copy)
        # change motion to linear
        cmds.selectKey("motionPath1_uValue") ## wouldn't it be repeated?
        cmds.keyTangent(inTangentType = "linear", outTangentType = "linear")
        # create empty folder to hold all duplicates created later
        self.folderName = cmds.promptDialog(query =  True, text = True)
        parentFolder = cmds.group(empty = True, name = self.folderName)
        # multiply road
        # determine the starting frame of the timeline
        self.minFrame = cmds.playbackOptions(query = True, min = True)
        for obj in range(int(self.minFrame), int(self.minFrame) + self.copy):
            # get attributes of the locator every frame
            cmds.currentTime(obj, edit = True)
            currentX = cmds.getAttr("rLoc.tx")
            currentY = cmds.getAttr("rLoc.ty")
            currentZ = cmds.getAttr("rLoc.tz")
            currentRotY = cmds.getAttr('rLoc.ry')
            
            # select the model that chosen for population
            cmds.select(self.userRoad, replace = True)
            
            # duplicate the mesh and set the translation according to locator
            tempObj = cmds.duplicate()
            cmds.setAttr(tempObj[0] + ".tx", currentX)
            cmds.setAttr(tempObj[0] + ".ty", currentY)
            cmds.setAttr(tempObj[0] + ".tz", currentZ)
            cmds.setAttr(tempObj[0] + ".ry", currentRotY)
            
            # parent all models created to the folder
            cmds.parent(tempObj[0], self.folderName, relative = False)  # let user name it
        
        # delete the dummy node
        cmds.select("rLoc")
        cmds.delete()
        
    def undo(self, *args):
        if self.default == True:
            # make road from scratch
            cmds.select(self.roadBase, replace=True)
            cmds.delete()
        else:
            # populate user road
            cmds.select(self.folderName, replace=True)
            cmds.delete()

########################################################## LIGHT
class Light(UI):
    def __init__(self, north, time, weather, dynamic, frameStart, frameEnd, timeStart, timeEnd, intensity, sunColor, terrain):
        
        self.north = north
        self.time = time
        self.weather = weather
        self.dynamic = dynamic
        self.frameStart = frameStart
        self.frameEnd = frameEnd
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.intensity = intensity
        self.sunColor = sunColor
        self.terrain = terrain
        
        # define additional variables
        self.mdNode = 0
        self.adlNode = 0
        self.newTerrain = 0
        self.rainEmitter = 0
        self.rainParticle = 0
        # executing functions
        self.create()
        
        
    def create(self, *args):
        # let user name their light
        cmds.promptDialog(title='Light Name', message='Name your light: ',
                                        text='sun', button='OK')
        self.sun = cmds.promptDialog(query = True, text=True)
        # create light
        cmds.directionalLight(name= self.sun, rotation=(90,0,0))
        cmds.setAttr("%sShape.color"%self.sun, self.sunColor[0], self.sunColor[1], self.sunColor[2])
        cmds.setAttr("%sShape.intensity"%self.sun, self.intensity)
        # define north direction
        self.northDir()
    
    def northDir(self, *args):
        # define north direction
        if self.dynamic == False:
            self.mdNode=cmds.shadingNode('multiplyDivide', asUtility=True)
            cmds.setAttr("%s.input1X"%self.mdNode, self.time)
            if self.north == 1:
                # change rotate x, create extra add node
                cmds.setAttr('%s.input2X'%self.mdNode, -15)
                self.adlNode = cmds.shadingNode('addDoubleLinear', asUtility=True)
                cmds.setAttr("%s.input1"%self.adlNode, 90)
                cmds.connectAttr("%s.outputX"%self.mdNode, "%s.input2"%self.adlNode, force=True)
                cmds.connectAttr('%s.output'%self.adlNode, '%s.rotateX'%self.sun, force=True)
            if self.north == 2:
                # change rotate x, create extra add node
                cmds.setAttr('%s.input2X'%self.mdNode, 15)
                self.adlNode = cmds.shadingNode('addDoubleLinear', asUtility=True)
                cmds.setAttr("%s.input1"%self.adlNode, 90)
                cmds.connectAttr("%s.outputX"%self.mdNode, "%s.input2"%self.adlNode, force=True)
                cmds.connectAttr('%s.output'%self.adlNode, '%s.rotateX'%self.sun, force=True)
            if self.north == 3:
                # change rotate z
                cmds.setAttr('%s.input2X'%self.mdNode, -15)
                cmds.connectAttr("%s.outputX"%self.mdNode,"%s.rotateZ"%self.sun, force=True)
            if self.north == 4:
                # change rotate z
                cmds.setAttr('%s.input2X'%self.mdNode, 15)
                cmds.connectAttr("%s.outputX"%self.mdNode,"%s.rotateZ"%self.sun, force=True)
        # if using dynamic light
        if self.dynamic == True:
            # check validation of frame and time range
            if self.frameEnd <= self.frameStart:
                raise Exception (" Start frame is greater than end frame! ")
            if self.timeEnd <= self.timeStart:
                raise Exception (" Start time is greater than end time! ")
            cmds.select(self.sun)
            # check north direction
            if self.north == 1:
                # key the starting rotation
                cmds.currentTime(self.frameStart)
                cmds.rotate(self.timeStart*-15, relative=True)
                cmds.setKeyframe()
                # key the ending rotation
                cmds.currentTime(self.frameEnd)
                cmds.rotate(self.timeEnd*-15, relative=True)
                cmds.setKeyframe()
            if self.north == 2:
                # key the starting rotation
                cmds.currentTime(self.frameStart)
                cmds.rotate(self.timeStart*15, relative=True)
                cmds.setKeyframe()
                # key the ending rotation
                cmds.currentTime(self.frameEnd)
                cmds.rotate(self.timeEnd*15, relative=True)
                cmds.setKeyframe()
            if self.north == 3:
                # key the starting rotation
                cmds.currentTime(self.frameStart)
                cmds.rotate(0,0,self.timeStart*-15, relative=True)
                cmds.setKeyframe()
                # key the ending rotation
                cmds.currentTime(self.frameEnd)
                cmds.rotate(0,0,self.timeEnd*-15, relative=True)
                cmds.setKeyframe()
            if self.north == 4:
                # key the starting rotation
                cmds.currentTime(self.frameStart)
                cmds.rotate(0,0,self.timeStart*15, relative=True)
                cmds.setKeyframe()
                # key the ending rotation
                cmds.currentTime(self.frameEnd)
                cmds.rotate(0,0,self.timeEnd*15, relative=True)
                cmds.setKeyframe()
            # create weather
            cmds.select(clear=True)
            self.weatherCon()


    def weatherCon(self, *args):        
        # define weather condition
        if self.weather == 1:
            print 'sunny'
            
        if self.weather == 2:
            print 'cloudly'
            # get the terrain bounding box
            bbox = cmds.exactWorldBoundingBox(self.terrain)
            # create cloud emitter
            cmds.Create3DContainerEmitter()
            cmds.rename("fluid1","cloud")
            cmds.select("cloud", replace=True)
            cmds.move(0, abs(bbox[0]*2), relative=True)
            # set the dimentions and resolutions
            cmds.setAttr("cloudShape.squareVoxels", 0)
            cmds.setAttr("cloudShape.dimensionsW", abs(bbox[0]*2))
            cmds.setAttr("cloudShape.dimensionsH", abs(bbox[0]*0.1))
            cmds.setAttr("cloudShape.dimensionsD", abs(bbox[0]*2))
            cmds.setAttr("cloudShape.resolution", abs(bbox[0]*5),abs(bbox[0]),abs(bbox[0]*5))
            # make the density to y gradient
            cmds.setAttr("cloudShape.densityMethod", 3) # can be zero
            cmds.setAttr("cloudShape.velocityMethod", 0)
            # shading
            cmds.setAttr("cloudShape.dropoffShape", 6)
            cmds.setAttr("cloudShape.edgeDropoff", 0.4)
            # color
            cmds.setAttr("cloudShape.color[0].color_Color", 0.4,0.4,0.4)
            cmds.setAttr("cloudShape.colorInput", 2)
            # opacity
            cmds.setAttr("cloudShape.opacity[2].opacity_FloatValue", 0.1)
            cmds.setAttr("cloudShape.opacity[2].opacity_Position", 0.5)
            cmds.setAttr("|cloud|cloudShape.opacity[3].opacity_FloatValue", 0.55)
            cmds.setAttr("|cloud|cloudShape.opacity[3].opacity_Position", 0.75)
            cmds.setAttr("|cloud|cloudShape.opacity[3].opacity_Interp", 1)
            # textures
            cmds.setAttr("cloudShape.opacityTexture", 1)
            cmds.setAttr("cloudShape.amplitude", 1.5)
            cmds.setAttr("cloudShape.depthMax", 5)
            cmds.setAttr("cloudShape.inflection", 1)
            # set key frame of texture time
            cmds.currentTime(self.frameStart)
            cmds.setAttr("cloudShape.textureTime", 1)
            cmds.setKeyframe("cloudShape.tti")
            cmds.currentTime(self.frameEnd)
            cmds.setAttr("cloudShape.textureTime", 4)
            cmds.setKeyframe("cloudShape.tti")
            # lighting
            cmds.setAttr("cloudShape.selfShadowing", 1)
        
        if self.weather == 3:
            print 'Rainy'
            # making the surface of particles
            self.newTerrain = cmds.duplicate(self.terrain, returnRootsOnly=True)[0]
            bbox = cmds.exactWorldBoundingBox(self.newTerrain)
            cmds.select(self.newTerrain)
            cmds.move(0, abs(bbox[0])*2, relative=True)
            cmds.rotate(180, relative=True, objectSpace=True, forceOrderXYZ=True)
            cmds.setAttr("%s.visibility"%self.newTerrain, 0)
            # create particles
            self.rainEmitter = cmds.emitter(type="surface", name="rain", rate=1000, scaleRateByObjectSize=False, 
                        needParentUV=False, cycleEmission="None", cycleInterval=1, 
                        speed=1, speedRandom=0, normalSpeed=1, tangentSpeed=0, maxDistance=0, minDistance=0, 
                        directionX=1, directionY=0, directionZ=0, spread=0)
            self.rainParticle = cmds.nParticle(name="rainParticle")
            cmds.connectDynamic("rainParticle", emitters="rain")
            # change particle shape
            cmds.setAttr("rainParticleShape.particleRenderType", 6)
            # change particle lifespan
            cmds.setAttr("rainParticleShape.lifespanMode", 2)
            cmds.setAttr("rainParticleShape.lifespan", abs(bbox[0])*0.5)
            # make particle collide with terrain
            cmds.select("rainParticle", replace=True)
            cmds.select(self.terrain, add=True)
            makecollide="makeCollideNCloth;"
            mel.eval(makecollide)
            cmds.select(clear=True)
            
        if self.weather == 4:
            print 'Snowy'
            # making the surface of particles
            self.newTerrain = cmds.duplicate(self.terrain, returnRootsOnly=True)[0]
            bbox = cmds.exactWorldBoundingBox(self.newTerrain)
            cmds.select(self.newTerrain)
            cmds.move(0, abs(bbox[0])*2, relative=True)
            cmds.rotate(180, relative=True, objectSpace=True, forceOrderXYZ=True)
            cmds.setAttr("%s.visibility"%self.newTerrain, 0)
            # create particles
            self.snowEmitter = cmds.emitter(type="surface", name="snow", rate=150, scaleRateByObjectSize=False, 
                        needParentUV=False, cycleEmission="None", cycleInterval=1, 
                        speed=0.25, speedRandom=0, normalSpeed=1, tangentSpeed=0, maxDistance=0, minDistance=0, 
                        directionX=1, directionY=0, directionZ=0, spread=0)
            self.snowParticle = cmds.nParticle(name="snowParticle")
            cmds.connectDynamic("snowParticle", emitters="snow")
            # change particle color and shape
            cmds.setAttr("snow.particleColor", 1,1,1)
            cmds.setAttr("snowParticleShape.particleRenderType", 8)
            cmds.setAttr("snowParticleShape.opacity", 0.3)
            # change particle lifespan
            cmds.setAttr("snowParticleShape.lifespanMode", 2)
            cmds.setAttr("snowParticleShape.lifespan", abs(bbox[0])*0.25)
            # make particle collide with terrain
            cmds.select("snowParticle", replace=True)
            cmds.select(self.terrain, add=True)
            makecollide="makeCollideNCloth;"
            mel.eval(makecollide)
            cmds.select(clear=True)
        
    def undo(self, *args):
        # delete light and nodes created
        cmds.delete(self.sun)
        if cmds.objExists(self.mdNode):
            cmds.delete(self.mdNode)
        if cmds.objExists(self.adlNode):
            cmds.delete(self.adlNode)
        if cmds.objExists(self.newTerrain):
            cmds.delete(self.newTerrain)
        # dynamic scene
        if cmds.objExists("cloud"):
            cmds.delete("cloud")        
        if cmds.objExists("rain"):
            cmds.delete("rain")
        if cmds.objExists("rainParticle"):
            cmds.delete("rainParticle")        
        if cmds.objExists("snowParticle"):
            cmds.delete("snowParticle")
        if cmds.objExists("nucleus1"):
            cmds.delete("nucleus1")
        if cmds.objExists("nRigid1"):
            cmds.delete("nRigid1")

################################## instance UI class ########################################
instanceUI = UI()
instanceUI.makeUI()

