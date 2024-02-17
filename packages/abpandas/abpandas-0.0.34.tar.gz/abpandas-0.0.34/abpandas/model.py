from .agent import Agent
import geopandas as gpd
import pandas as pd
import numpy
from shapely import geometry, distance
import fiona
import copy

class Model:

    def __init__ (self, space: gpd.GeoDataFrame, agents= []):
        """
        A class containing the GIS map and all the agents

        Attributes
        ----------
        space: geopandas object
            a spatial map with polygons read as a geopandas object
        agents: list of Agent objects, default= []
            a list of agents currently in the model
        
        Methods
        -------
        create_agent(properties= {})
            Create an agent with an input dictionary of properties
        agents_with_id(id)
            Search for agents by id
        agents_with_props(condition):
            Search for agents based on its properties
        agents_at(loc_index)
            Find agents based on their location index
        move_agents(agents, new_loc_index)
            Move an agent to a new location
        remove_agents(agents)
            Removes agents from the model
        save_space(file_directory)
            Saves the space to a shape file name
        """
        self.space = space
        self.space["agents"] = [list() for i in range(len(self.space.index))]
        self.space["n_agents"] = [len(self.space.at[i, "agents"]) for i in range(len(self.space.index))]
        self.agents = agents
        self.__id_counter = 0
        self.__classes = list()
        for a in self.agents:
            if self.__id_counter < a.id:
                self.__id_counter = a.id
            if a.my_class is not None and a.my_class not in self.__classes:
                self.__classes.append(a.my_class)
        
    def create_agent(self, properties= {}):
        """
        Create an agent with an input dictionary of properties

        Parameters
        ----------
        properties: dictionary, default= {}
            a dictionary of the properties of agents

        Returns
        -------
        Agent object
            the created Agent object
        """
        a_temp = Agent(properties)
        a_temp.id = self.__id_counter
        self.__id_counter += 1
        self.agents.append(a_temp)
        if a_temp.my_class is not None and a_temp.my_class not in self.__classes:
            self.__classes.append(a_temp.my_class)
        return(a_temp)

    def create_agents(self, N:int, properties={}):
        """
        Create a number of agents of type abp.Agent with an input dictionary of properties
        To create agents of a subclass from abp.Agent in the model, use add_agents() instead

        Parameters
        ----------
        N: int
            the number of agents

        properties: dictionary, default= {}
            a dictionary of the properties of agents

        Returns
        -------
        list of Agent objects
            the created Agents
        """
        created_agents = list()
        for n in range(N):
            a_temp = Agent(properties)
            a_temp.id = self.__id_counter
            self.__id_counter += 1
            self.agents.append(a_temp)
            created_agents.append(a_temp)
            self._manage_class_variables_add_agent(a_temp)
        return(created_agents)

    def add_agent(self, agent:Agent, loc_index:int= None):
        """
        add one agent to the model

        Parameters
        ----------
        agent: Agent
            a previously created agent
        
        loc_index: int, default= None
            the index of the patch at which the agent is places

        Returns
        -------
        N/A
        """

        try:
            agent.id = self.__id_counter
            self.__id_counter += 1
            self.agents.append(agent)
            if loc_index is not None:
                self.space.at[loc_index, "agents"].append(agent)
                self.space.at[loc_index, "n_agents"] += 1
                agent.location_index = loc_index
            self._manage_class_variables_add_agent(agent)
        except:
            print("Error: check that the object in the agents list is of type or a child of Agent")


    def add_agents(self, agents:list or Agent, loc_index:int= None):
        """
        add agents to the model

        Parameters
        ----------
        agent: Agent
            a previously created agent
        
        loc_index: int, default= None
            the index of the patch at which the agent is places

        Returns
        -------
        N/A
        """
        if type(agents) == list:
            try:
                for a in agents:
                    self.add_agent(a, loc_index)
            except:
                print("Error: check that all objects in the agents list are of type or children of Agent")

        else:
            self.add_agent(agents, loc_index)
            
    def agents_with_id(self, id: int):
        """
        Search for agents by id

        Parameters
        ----------
        id: int or list
            the id(s) of the agent to search for

        Returns
        -------
        an Agent object (if id is int) or a list of Agent objects (if id is list)
            the Agent(s) with the provided id(s)

        """
        try:
            if type(id) is int:
                for a in self.agents:
                    if a.id == id:
                        return a
    
            elif type(id) is list:
                list_temp = []
                for a in self.agents:
                    for id_temp in id:
                        if a.id == id_temp:
                            list_temp.append(a)
                return list_temp
        
        except:
            print("Error: Invalid ID")

    def agents_with_props(self, condition: str or function):
        """
        Search for agents based on their properties

        Parameters
        ----------
        condition: str
            a string representing a condition to be evaluated across all agents in the model
            the properties are accessed as `agent.props["property_name"]`
        
        condition: function
            a function taking in an abp.Agent and returning true if the condition is satisfied


        Returns
        -------
        list of Agent objects
            the list of Agent objects fulfilling the condition
        """
        list_temp = []
        for agent in self.agents:
            if eval(condition):
                list_temp.append(agent)
        return list_temp
    
    def agents_at(self, loc_index: str):
        """
        Find all the agents based on their location index

        Parameters
        ----------
        loc_index: int
            the index of the polygon in the space
        
        Returns
        -------
        list of Agent objects
            list of Agent objects located in input index
        """
        return(self.space.at[loc_index, 'agents'])

    def move_agent(self, agent: Agent, new_loc_index: int):
        """
        Move an agent to a new location

        Parameters
        ----------
        agents: list of Agent objects or an Agent object
            the agents to move to a new location
        new_loc_index: int
            the index of the polygon in the sapce to which agents will move
        
        Returns
        -------
        N/A
        """
        try:
            if agent.location_index is not None:
                self.space.at[agent.location_index, "agents"].remove(agent)
                self.space.at[agent.location_index, "n_agents"] -= 1
                self._manage_class_variables_remove_agent(agent)
            
            agent.location_index = new_loc_index
            self.space.at[new_loc_index, "agents"].append(agent)
            self.space.at[new_loc_index, "n_agents"] += 1
            self._manage_class_variables_add_agent(agent)
        except:
            print("Error: type of agent variable is not Agent")

    def move_agents(self, agents: list or Agent, new_loc_index: int):
        """
        Move an agent or a group of agents to a new location

        Parameters
        ----------
        agent: Agent object
            the agent to move to a new location
        new_loc_index: int
            the index of the polygon in the sapce to which agents will move
        
        Returns
        -------
        N/A
        """
        if type(agents) is list:
            for agent in agents:
                self.move_agent(agent, new_loc_index)
        else:
            agent = agents
            self.move_agent(agent, new_loc_index)

    def remove_agent(self, agent: Agent):
        """
        Removes agents from the model

        Parameters
        ----------
        agents: list of Agent objects or an Agent object
            the agents to remove from the model
        
        Returns
        -------
        N/A
        """
        #try:
        if agent.location_index is not None:
            self.space.at[agent.location_index, 'agents'].remove(agent)
            self.space.at[agent.location_index, "n_agents"] -= 1
        self.agents.remove(agent)
        self._manage_class_variables_remove_agent(agent)
        
        #except:
        #    print('Error abp.remove_agent(): agent variable is not of type Agent')
    
    def remove_agents(self, agents: list or Agent):
        """
        Removes agents from the model

        Parameters
        ----------
        agents: list of Agent objects or an Agent object
            the agents to remove from the model
        
        Returns
        -------
        N/A
        """
        try:
            if type(agents) is list:
                for agent in agents:
                    self.remove_agent(agent)
            
            else:
                agent = agents
                self.remove_agent(agent)
        
        except:
            print('Error: agents are not of type Agent or a list of objects of type Agent')

    def save_space(self, file_directory: str):
        """
        Saves the space to a shape file name

        Parameters
        ----------
        file_directory: str
            the full directory of the file to be saved (should end in .shp or .pkl)
        
        Returns
        -------
        N/A
        """
        temp_space = copy.deepcopy(self.space)
        if file_directory[-3:] == 'pkl':
            temp_space.to_pickle(rf'{file_directory}')
        elif file_directory[-3:] == 'shp':
            for c in temp_space.columns:
                for i in temp_space.index:
                    if type(temp_space.at[i, c]) is list:
                        temp_space.at[i, c] = str(temp_space.at[i, c])
            temp_space.to_file(rf'{file_directory}')
        else:
            return('Error: Invalid file type. Insert .shp or .pkl at the end of your file directory string')
        
    def index_at_ij(self, i: int, j: int):
        """
        Finds the patches based on their i and j location (i and j are the indices of a patch in x-direction and y-direction respectively).
        i and j are created during the create_patches() function.

        Parameters
        ----------
        i: int
            the index of the patch in x-direction (starts from 1)
        j: int
            the index of the patch in y-direction (starts from 1)
        
        Returns
        -------
        int
            index of the polygon in the abpandas.space geodataframe
        """
        try:
            temp_index_a = self.space[self.space['i'] == i]
            temp_index_b = temp_index_a[temp_index_a['j'] == j]
            return temp_index_b.index[0]
        except:
            print("Error: invalid i or j")
    
    def indices_in_radius(self, centre: Agent or int or geometry.polygon.Polygon, radius: int or float, outline_only: bool=False, return_patches=False):
        """
        finds the patches (polygons) within a given radius

        Parameters
        ----------
        centre: Agent or int or a shapely polygon
            central agent, patch index or shapely polygon
        radius: int or float
            the radius from the centre
        outline_only: bool, default=False
            limit the outcome to the outline of the create_space generated polygons
        return_patches: bool, default=False
            return a list of shapely geometries instead of indices
        
        Returns
        -------
        list of indeces (if return_patches=False)
            index of the polygons within the radius in Model.space
        list of shapely polygons (if return_patches=True)
            the polygons within the radius in Model.space
        """
        # polygons
        try:
            if type(centre) == geometry.polygon.Polygon:
                # find the centre of the polygon and create a buffer circle
                centre_point = centre.centroid
            # indices
            elif type(centre) == int:
                centre_polygon = self.space.at[centre, "geometry"]
                centre_point = centre_polygon.centroid
            else:
                centre_polygon = self.space.at[centre.location_index, "geometry"]
                centre_point = centre_polygon.centroid
        except ValueError:
            print("Error: cannot generate centroid point from centre input")
        # create a circle and empty lists to return
        circle = centre_point.buffer(radius)
        p_in_radius = list()
        i_in_radius = list()
        # check all geometries in the space
        for i in self.space.index:
            # include all polygons within the circle
            if outline_only == False:
                if circle.contains(self.space.at[i, "geometry"]):
                    p_in_radius.append(self.space.at[i, "geometry"])
                    i_in_radius.append(i)
            # include polygons intersecting with the circle (find polygon boundary lines and check intersection)
            else:
                boundaries = circle.boundary
                if boundaries.intersects(self.space.at[i, "geometry"]):
                    p_in_radius.append(self.space.at[i, "geometry"])
                    i_in_radius.append(i)
        if return_patches == True:
            return p_in_radius
        else:
            return i_in_radius

    def indexes_in_radius(self, centre: Agent or int or geometry.polygon.Polygon, radius: int or float, outline_only: bool=False, return_patches=False):
        """
        finds the patches (polygons) within a given radius

        Parameters
        ----------
        centre: Agent or int or a shapely polygon
            central agent, patch index or shapely polygon
        radius: int or float
            the radius from the centre
        outline_only: bool, default=False
            limit the outcome to the outline of the create_space generated polygons
        return_patches: bool, default=False
            return a list of shapely geometries instead of indices
        
        Returns
        -------
        list of indeces (if return_patches=False)
            index of the polygons within the radius in Model.space
        list of shapely polygons (if return_patches=True)
            the polygons within the radius in Model.space
        """
        self.indices_in_radius(centre, radius, outline_only, return_patches)
    
    def distance(self, a:Agent or int or geometry.polygon.Polygon, b:Agent or int or geometry.polygon.Polygon):
        """
        finds the distance between patches and agents

        Parameters
        ----------
        a: Agent, index or shapely polygon
            the first object
        
        b: Agent, index or shapely polygon
            the second object
        
        Returns
        -------
        float
            distance (units depends on shapefile)
        """
        if type(a) == int:
            patch_a = self.space.at[a, "geometry"]
            
        elif type(a) == geometry.polygon.Polygon:
            patch_a = a
        else:
            patch_a = self.space.at[a.location_index, "geometry"]
        
        if type(b) == int:
            patch_b = self.space.at[b, "geometry"]
            
        elif type(b) == geometry.polygon.Polygon:
            patch_b = b
        else:
            patch_b = self.space.at[b.location_index, "geometry"]

        centre_a = patch_a.centroid
        centre_b = patch_b.centroid
        return distance(centre_a, centre_b)


    def _manage_class_variables_add_agent(self, agents: list or Agent):
        """
        Check if the class of the agent is in the model, create space and Model variables and count the agents by class.
        Forces all created variables to a lowercase.

        Parameters
        ----------
        agent: Agent
            the agent with the class to check

        Returns
        -------
        boolean
            True if the class is found and False if not
        """
        if type(agents) == list:
            try:
                for agent in agents:
                    # if the class has not been added before
                    if agent.my_class is not None and agent.my_class not in self.__classes:
                        # add the class to the list __classes
                        self.__classes.append(agent.my_class)
                        # add the class to the geodataframe and the list of Model variables in __dict__
                        name_p_l = f"{self.__classes[-1]}s".lower()
                        self.space[name_p_l] = [list() for i in range(len(self.space.index))]
                        self.space[f"n_{name_p_l}"] = [0 for i in range(len(self.space.index))]
                        self.__dict__[name_p_l] = [agent]
                        if agent.location_index is not None:
                            self.space.at[agent.location_index, name_p_l].append(agent)
                            self.space.at[agent.location_index, f"n_{name_p_l}"] += 1
                        return False
                    # if the class has already been added
                    elif agent.my_class in self.__classes:
                        name_p_l = f"{agent.my_class}s".lower()
                        if agent not in self.__dict__[name_p_l]:
                            self.__dict__[name_p_l].append(agent)
                        if agent.location_index is not None:
                            self.space.at[agent.location_index, name_p_l].append(agent)
                            self.space.at[agent.location_index, f"n_{name_p_l}"] += 1
                        return True
            except:
                print("Error: check that all objects in the agents list are of type or children of Agents")
        else:
            try:
                agent = agents
                # if the class has not been added before
                if agent.my_class is not None and agent.my_class not in self.__classes:
                    # add the class to the list __classes
                    self.__classes.append(agent.my_class)
                    # add the class to the geodataframe and the list of Model variables in __dict__
                    name_p_l = f"{self.__classes[-1]}s".lower()
                    self.space[name_p_l] = [list() for i in range(len(self.space.index))]
                    self.space[f"n_{name_p_l}"] = [0 for i in range(len(self.space.index))]
                    self.__dict__[name_p_l] = [agent]
                    if agent.location_index is not None:
                        self.space.at[agent.location_index, name_p_l].append(agent)
                        self.space.at[agent.location_index, f"n_{name_p_l}"] += 1
                    return False
                # if the class has already been added
                elif agent.my_class in self.__classes:
                    name_p_l = f"{agent.my_class}s".lower()
                    if agent not in self.__dict__[name_p_l]:
                        self.__dict__[name_p_l].append(agent)
                    if agent.location_index is not None:
                        self.space.at[agent.location_index, name_p_l].append(agent)
                        self.space.at[agent.location_index, f"n_{name_p_l}"] += 1
                    return True
            except:
                print("Error: check that the agents input variable is either an Agent or a list of Agents")

    def _manage_class_variables_remove_agent(self, agents: list or Agent):
        """
        Manage the class space and Model variables when removing an agent.

        Parameters
        ----------
        agent: Agent
            the agent to remove from the model

        Returns
        -------
        N/A
        """
        try:
            if type(agents) == list:
                for agent in agents:
                    name_p_l = f"{agent.my_class}s".lower()
                    self.__dict__[name_p_l].remove(agent)
                    if agent.location_index is not None:
                        self.space.at[agent.location_index, name_p_l].remove(agent)
                        self.space.at[agent.location_index, f"n_{name_p_l}"] -= 1
            else:
                agent = agents
                name_p_l = f"{agent.my_class}s".lower()
                self.__dict__[name_p_l].remove(agent)
                if agent.location_index is not None:
                    self.space.at[agent.location_index, name_p_l].remove(agent)
                    self.space.at[agent.location_index, f"n_{name_p_l}"] -= 1
        except:
            print("Error: check that the agents input variable is either an Agent or a list of Agents")

