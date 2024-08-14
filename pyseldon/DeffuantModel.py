"""
Deffuant Model
--------------

This is the implementation of the Deffuant Model in Opinion Dynamics.

In this model, referred to as "Mixing of Beliefs among Interacting Agents" in various papers, agents adjust their continuous opinions through random binary encounters, provided their difference in opinion is below a given threshold known as the Homophily Threshold.

High thresholds lead to the convergence of opinions towards an average opinion, while low thresholds result in the formation of several opinion clusters. Members of the same cluster share a similar opinion but are no longer influenced by members of other clusters.

Example:
---------
>>> from pyseldon import DeffuantModel
>>> # Create the Deffuant Model
>>> deffuant = DeffuantModel(max_iterations=1000, homophily_threshold=0.2, mu=0.5)
>>> # Run the simulation
>>> deffuant.run("output_dir")
>>> # Access the network
>>> network = deffuant.get_Network()
>>> # Access the opinions of the agents
>>> opinions = deffuant.agents_opinions()

read also: Network, Other_Settings

Reference:
----------
- Mixing beliefs among interacting agents. Guillaume Deffuant, David Neau, Frédéric Amblard, and Gérard Weisbuch. Advances in Complex Systems, 3(1-4):87-98, 2000. DOI: 10.1142/S0219525900000078
"""

from bindings import seldoncore
import pathlib
from typing import Optional

from ._othersettings import Other_Settings


class Deffuant_Model:
    """
    Deffuant Model base class for Simulation.

    Parameters
    -----------
    max_iterations : int, default=None
      The maximum number of iterations to run the simulation. If None, the simulation runs infinitely.

    homophily_threshold : float, default=0.2
      The threshold for homophily. If the difference in opinions between two agents is less than this value, they interact.

    mu : float, default=0.5
      The convergence rate of the agents.

    use_network : bool, default=False
      For using a square lattice network. Will throw error if sqrt(n_agents) is not an integer.

    rng_seed : int, default=None
      The seed for the random number generator. If not provided, a random seed is picked.

    agent_file : str, default=None
      The file to read the agents from. If None, the agents are generated randomly.

    network_file : str, default=None
      The file to read the network from. If None, the network is generated randomly

    other_settings : Other_Settings, default=None
      The other settings for the simulation. If None, the default settings are used.

    Attributes
    -----------
    Network : Network (Object)
      The network generated by the simulation.

    Opinion : Float
      The opinions of the agents or nodes of the network.

    see also: seldoncore.Network
    """

    def __init__(
        self,
        max_iterations: int = None,
        homophily_threshold: float = 0.2,
        mu: float = 0.5,
        use_network: bool = False,
        rng_seed: Optional[int] = None,
        agent_file: Optional[str] = None,
        network_file: Optional[str] = None,
        other_settings: Other_Settings = None,
    ):  
        self.other_settings = Other_Settings()
        if other_settings is not None:
            self.other_settings = other_settings

        self._options = seldoncore.SimulationOptions()
        self._options.model_string = "Deffuant"
        self._options.model_settings = seldoncore.DeffuantSettings()
        self._options.output_settings = self.other_settings.output_settings
        self._options.network_settings = self.other_settings.network_settings
        self._options.model = seldoncore.Model.DeffuantModel

        if rng_seed is not None:
            self._options.rng_seed = rng_seed
        
        self._options.model_settings.max_iterations = max_iterations
        self._options.model_settings.homophily_threshold = homophily_threshold
        self._options.model_settings.mu = mu
        self._options.model_settings.use_network = use_network
        self._options.model_settings.use_binary_vector = False


        self._simulation = seldoncore.SimulationSimpleAgent(
            options=self._options,
            cli_agent_file=agent_file,
            cli_network_file=network_file
        )

        self.Network = self._simulation.network

    def run(self, output_dir: str = None):
        """
        Run the simulation.

        Parameters
        -----------
        output_dir : str, default="./output"
          The directory to output the files to.
        """
        seldoncore.validate_settings(self._options)
        seldoncore.print_settings(self._options)
        cwd = pathlib.Path.cwd()
        if output_dir is None:
            output_dir = "./output"
        output_path = cwd / pathlib.Path(output_dir)
        if output_path.exists():
          raise Exception("Output Directory already Exists!! Either delete it or change the path!!")
        print(f"Output directory path set to: {output_path}\n")
        output_path.mkdir(parents=True, exist_ok=True)
        self._simulation.run(output_dir )
        self.Network = self._simulation.network

    def print_settings(self):
        """
        Print the settings of the simulation.
        """
        seldoncore.print_settings(self._options)

    def get_Network(self):
        """
        Access the network generated by the simulation.

        Returns
        --------
        seldoncore.Network
          The network generated by the simulation.
        """
        return self.Network

    def agent_opinion(self, index: int = None):
        """
        Access the agents data from the simulation.

        Parameters
        -----------
        index : int
          The index of the agent to access. The index is 0-based. If not provided, all agents are returned.
        """
        if index is None:
            result = [agent.data.opinion for agent in self._simulation.network.agent]
            return result
        else:
            if index < 0 or index >= self.Network.n_agents():
              raise IndexError("Agent index is out of range.")
            return self._simulation.network.agent[index].data.opinion

    def set_agent_opinion(self, index: int, opinion: float):
        """
        Set the opinion of a specific agent.

        Parameters
        ----------
        index : int
            The index of the agent whose opinion is to be set.
        opinion : float
            The new opinion value for the agent.
        """        
        if index < 0 or index >= self.Network.n_agents():
            raise IndexError("Agent index is out of range.")
        
        self._simulation.network.agent[index].data.opinion = opinion

    def __getattr__(self, name):
        if '_options' in self.__dict__ and hasattr(self.__dict__['_options'].model_settings, name):
            return getattr(self.__dict__['_options'].model_settings, name)
        elif name == "rng_seed":
            return self.__dict__['_options'].rng_seed
        elif name == "other_settings":
            return self.__dict__['other_settings']
        else:
            return self.__dict__[name]

    def __setattr__(self, name, value):
        if '_options' in self.__dict__ and hasattr(self.__dict__['_options'].model_settings, name):
            setattr(self.__dict__['_options'].model_settings, name, value)
        elif name == "rng_seed":
            self.__dict__['_options'].rng_seed = value
        elif name == "other_settings":
            self.__dict__['other_settings'] = value
        else:
            self.__dict__[name] = value