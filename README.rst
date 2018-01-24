=====
RemoteReplayHMMs
=====

Identification of remote replay using hidden Markov models from "`Latent Variable Models for Hippocampal Sequence Analysis <https://github.com/kemerelab/RemoteReplayHMMs/blob/master/asilomar2017.pdf>`_" by **Etienne Ackermann, Kourosh Maboudi, Kamran Diba, & Caleb Kemere**, *Asilomar Conference on Signals, Systems, and Computers*, Pacific Grove, CA, October 29–November 1, 2017.

Overview
========
The activity of ensembles of neurons within the hippocampus is thought to enable memory formation, storage, recall, and potentially decision making. During offline states (associated with sharp wave ripples, quiescence, or sleep), some of these neurons are reactivated in temporally-ordered sequences which are thought to enable associations across time and episodic memories spanning longer periods. However, analyzing these sequences of neural activity remains challenging. Here we build on recent approaches using latent variable models for hippocampal population codes, to detect so-called “replay events”, and to build models of hippocampal sequences independent of animal behavior. We demonstrate that our approach can identify the same replay events as traditional Bayesian decoding approaches, and moreover, that it can detect nonlinear remote replay events that are difficult or impossible to detect with existing approaches.

More specifically, we analyze data obtained from CRCNS.org (https://crcns.org/data-sets/hc/hc-6), and reproduce several of the results from https://www.nature.com/articles/nn.2344, and we demonstrate how we can use HMMs to perform a similar remote replay analysis.

For more information, see the conference `paper <https://github.com/kemerelab/RemoteReplayHMMs/blob/master/asilomar2017.pdf>`_.

This analysis makes extensive use of ``nelpy`` (https://github.com/nelpy/nelpy).

.. raw:: html

    <img src="https://raw.githubusercontent.com/kemerelab/RemoteReplayHMMs/master/.overview.png" width="60px", align="center">
