import numpy as np
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.preprocessing import normalize
from reach import Reach
from collections import Counter

class CAt():
    """
    Implementation of Contrastive Attention Topic Modeling describe in "Embarrassingly Simple Unsupervised Aspect Extraction"
    
    URL : https://aclanthology.org/2020.acl-main.290

    Calculating attribution topic scores for a list of tokens.
    Scores are computed using an approach based on RBF (Radial Basis Function) similarity functions between tokens and candidate aspects, 
    and then using attention to aggregate scores of topics associated with candidate aspects.
    """

    def __init__(self, r: Reach, gamma: float = .03, norm: str = "l2") -> None:
        """
        Parameters:
        -----------
        - r (Reach) : A reach instance for compute word embeddings
        - gamma (float) : Gamma parameter of RBF similarity function (default 0.03)
        - norm (str) : The norm to use for normalization (default "l2", see scikit-learn)
        """
        self.r = r
        self.gamma = gamma
        self.norm = norm
        self.aspects_matrix = None
        self.topics = []
        self.topics_matrix = None

    def init_candidate_aspects(self, aspects: list[str]) -> None:
        """
        Initialize candidate aspects

        Parameters:
        -----------
        - aspects (list[str]) : List of aspects as candidates
        """
        self.aspects_matrix = np.array([self.r[a] for a in aspects])
    
    def add_topic(self, label: str, aspects: list[str]) -> None:
        """
        Add topic and compute its vector based on its composition (mean vector of multiple aspects)

        Parameters:
        -----------
        - topic (str) : Name of topic
        - aspects (list[str]) : List of aspects that compose the topic
        """

        self.topics.append(label)
        topic_vector = normalize(np.mean([self.r[a] for a in aspects], axis=0).reshape(1, -1), norm=self.norm)
        if self.topics_matrix is None: self.topics_matrix = topic_vector
        else: self.topics_matrix = np.vstack((self.topics_matrix, topic_vector.squeeze()))
    
    def get_scores(self, tokens: list[str], remove_oov=True) -> list[(str,float)]:
        """
        Compute the score of each topics

        Parameters:
        -----------
        - tokens (list[str]) : A list of tokens for which to compute scores.
        - remove_oov (bool) : Indicates whether to remove out-of-vocabulary tokens (default True).

        Returns:
        --------
        - list(tuple(str, float)) : A list of tuples containing labels and their associated scores, 
          sorted in descending order of score.
        """

        assert self.aspects_matrix is not None, "No candidate aspects have been initialized"
        assert len(self.topics) > 0, "No labels have been added"

        score = Counter({topic: 0 for topic in self.topics})
        tokens_matrix = self.r.vectorize(tokens, remove_oov=remove_oov)
        if len(tokens_matrix) == 0: return score.most_common()

        rbf_similarity = np.exp(rbf_kernel(tokens_matrix, self.aspects_matrix, gamma=self.gamma))
        sum_rbf_similarity = rbf_similarity.sum()
        if sum_rbf_similarity == 0: return score.most_common()
        att_vector = (rbf_similarity.sum(axis=1) / sum_rbf_similarity).squeeze()

        tokens_att_matrix = att_vector.dot(tokens_matrix).reshape(1, -1)
        labels_att_matrix = normalize(tokens_att_matrix, norm=self.norm).dot(self.topics_matrix.T)
        scores = labels_att_matrix.sum(axis=0)

        for i, topic in enumerate(self.topics):
            score[topic] = scores[i]
        return score.most_common()