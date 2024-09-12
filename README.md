
# Stratum BTC Miner

This is a pure python Stratum protocol based BTC pool miner. Its true use is educational and not mining as it's super slow. Currently the project is still under heavy construction and there is much todo until it reaches it's full educational glory. If this project has helped you in any way shape of form please start it! ♥

<p align="center">
  <img width=350 height=350 src="https://github.com/B-aublys/stratum_btc_miner/blob/main/picture/Leonardo_Phoenix_A_wispybearded_fire_wizard_with_a_fieryorange_1%20smaller.jpg">
</p>

<p align="center">
  How Powerful is your Wizard?
</p>
<p align="center">
  <img width=350 src="https://github.com/B-aublys/stratum_btc_miner/blob/main/picture/Wizzards%20power.png">
</p>

## Roadmap

* [ ]  Test the miner implementation on a testnet pool (requires self hosting)
* [x]  Add the Hash-Rate measurements
* [x]  Implement better process handling
    * [x]  Clean closing all the Processes when the program gets stopped
    * [x]  Each time new data gets sent from the server perhaps not restarting all the mining processes.
* [ ]  Create a better and more informative user interface
* [ ]  Create diagrams explaining the structure of the code
* [ ]  Create a youtube video explaining each step of the miner 😄
* [ ]  GPU acceleration!




## Documentation 👷‍♂️

### Main Sources of information:

The Stratum protocol Wiki: [Wiki](https://en.bitcoin.it/wiki/Stratum_mining_protocol#mining.notify)

Some other python miners, sorry I can't name them here, because I have forgoten what I used for what, but there are quite some!

### Usage:

Clone the repo, configure your own settings in `/config.py` file and run:

    python .\demist_stratum_miner.py


### Software Structure overview
Here is a diagram representing all the processes, classes and their interaction between each other! All the colored blocks are processes that run continuesly throughout the execution of the program.

<p align="center">
  <img src="https://github.com/B-aublys/stratum_btc_miner/blob/main/picture/Software_diagram2.png">
</p>
<p align="center">
  <a href="https://excalidraw.com/#json=X4kG-XapCy7Zmb1supaOb,cY05_F5dvvUpeuprZP8IIQ">Link to diagram</a>
</p>

🚧 The rest of the documentation is under construction! 🏗



## Acknowledgements

 - [The AI generated wizzard picture is from Leonardo.ai](https://leonardo.ai/)


