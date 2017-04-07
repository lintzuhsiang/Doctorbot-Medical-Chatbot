# Adapted from tensorflow/models/tutorials/rnn/translate/data_utils.py
# https://github.com/tensorflow/models/blob/master/tutorials/rnn/translate/data_utils.py
# ==============================================================================

"""Utilities for tokenizing and vocabularies."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import random
import numpy as np
import sys

from tensorflow.python.platform import gfile
import tensorflow as tf

# Special vocabulary symbols - we always put them at the start.
_PAD = b"_PAD"
_GO = b"_GO"
_EOS = b"_EOS"
_UNK = b"_UNK"
_START_VOCAB = [_PAD, _GO, _EOS, _UNK]

PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3

# Regular expressions used to tokenize.
_WORD_SPLIT = re.compile(b"([.,!?\"':;)(])")
_DIGIT_RE = re.compile(br"\d")


def basic_tokenizer(sentence):
  """Very basic tokenizer: split the sentence into a list of tokens."""
  words = []
  for space_separated_fragment in sentence.strip().split():
    words.extend(_WORD_SPLIT.split(space_separated_fragment))
  return [w for w in words if w]


def create_vocabulary(vocabulary_path, data_path, max_vocabulary_size,
                      tokenizer=None, normalize_digits=True):
  """Create vocabulary file (if it does not exist yet) from data file.

  Data file is assumed to contain one sentence per line. Each sentence is
  tokenized and digits are normalized (if normalize_digits is set).
  Vocabulary contains the most-frequent tokens up to max_vocabulary_size.
  We write it to vocabulary_path in a one-token-per-line format, so that later
  token in the first line gets id=0, second line gets id=1, and so on.

  Args:
    vocabulary_path: path where the vocabulary will be created.
    data_path: data file that will be used to create vocabulary.
    max_vocabulary_size: limit on the size of the created vocabulary.
    tokenizer: a function to use to tokenize each data sentence;
      if None, basic_tokenizer will be used.
    normalize_digits: Boolean; if true, all digits are replaced by 0s.
  """
  if not gfile.Exists(vocabulary_path):
    print("Creating vocabulary %s from data %s" % (vocabulary_path, data_path))
    vocab = {}
    with gfile.GFile(data_path, mode="rb") as f:
      counter = 0
      for line in f:
        counter += 1
        if counter % 100000 == 0:
          print("  processing line %d" % counter)
        line = tf.compat.as_bytes(line)
        tokens = tokenizer(line) if tokenizer else basic_tokenizer(line)
        for w in tokens:
          word = _DIGIT_RE.sub(b"0", w) if normalize_digits else w
          if word in vocab:
            vocab[word] += 1
          else:
            vocab[word] = 1
      vocab_list = _START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
      if len(vocab_list) > max_vocabulary_size:
        vocab_list = vocab_list[:max_vocabulary_size]
      with gfile.GFile(vocabulary_path, mode="wb") as vocab_file:
        for w in vocab_list:
          vocab_file.write(w + b"\n")


def initialize_vocabulary(vocabulary_path):
  """Initialize vocabulary from file.

  We assume the vocabulary is stored one-item-per-line, so a file:
    dog
    cat
  will result in a vocabulary {"dog": 0, "cat": 1}, and this function will
  also return the reversed-vocabulary ["dog", "cat"].

  Args:
    vocabulary_path: path to the file containing the vocabulary.

  Returns:
    a pair: the vocabulary (a dictionary mapping string to integers), and
    the reversed vocabulary (a list, which reverses the vocabulary mapping).

  Raises:
    ValueError: if the provided vocabulary_path does not exist.
  """
  if gfile.Exists(vocabulary_path):
    rev_vocab = []
    with gfile.GFile(vocabulary_path, mode="rb") as f:
      rev_vocab.extend(f.readlines())
    rev_vocab = [tf.compat.as_bytes(line.strip()) for line in rev_vocab]
    vocab = dict([(x, y) for (y, x) in enumerate(rev_vocab)])
    return vocab, rev_vocab
  else:
    raise ValueError("Vocabulary file %s not found.", vocabulary_path)


def sentence_to_token_ids(sentence, vocabulary,
                          tokenizer=None, normalize_digits=True):
  """Convert a string to list of integers representing token-ids.

  For example, a sentence "I have a dog" may become tokenized into
  ["I", "have", "a", "dog"] and with vocabulary {"I": 1, "have": 2,
  "a": 4, "dog": 7"} this function will return [1, 2, 4, 7].

  Args:
    sentence: the sentence in bytes format to convert to token-ids.
    vocabulary: a dictionary mapping tokens to integers.
    tokenizer: a function to use to tokenize each sentence;
      if None, basic_tokenizer will be used.
    normalize_digits: Boolean; if true, all digits are replaced by 0s.

  Returns:
    a list of integers, the token-ids for the sentence.
  """

  if tokenizer:
    words = tokenizer(sentence)
  else:
    words = basic_tokenizer(sentence)
  if not normalize_digits:
    return [vocabulary.get(w, UNK_ID) for w in words]
  # Normalize digits by 0 before looking words up in the vocabulary.
  return [vocabulary.get(_DIGIT_RE.sub(b"0", w), UNK_ID) for w in words]


def data_to_token_ids(data_path, target_path, vocabulary_path,
                      tokenizer=None, normalize_digits=True):
  """Tokenize data file and turn into token-ids using given vocabulary file.

  This function loads data line-by-line from data_path, calls the above
  sentence_to_token_ids, and saves the result to target_path. See comment
  for sentence_to_token_ids on the details of token-ids format.

  Args:
    data_path: path to the data file in one-sentence-per-line format.
    target_path: path where the file with token-ids will be created.
    vocabulary_path: path to the vocabulary file.
    tokenizer: a function to use to tokenize each sentence;
      if None, basic_tokenizer will be used.
    normalize_digits: Boolean; if true, all digits are replaced by 0s.
  """
  if not gfile.Exists(target_path):
    print("Tokenizing data in %s" % data_path)
    vocab, _ = initialize_vocabulary(vocabulary_path)
    with gfile.GFile(data_path, mode="rb") as data_file:
      with gfile.GFile(target_path, mode="w") as tokens_file:
        counter = 0
        for line in data_file:
          counter += 1
          if counter % 100000 == 0:
            print("  tokenizing line %d" % counter)
          token_ids = sentence_to_token_ids(tf.compat.as_bytes(line), vocab,
                                            tokenizer, normalize_digits)
          tokens_file.write(" ".join([str(tok) for tok in token_ids]) + "\n")


def read_data(source_path, target_path, max_size=None):
    dataset_x = []; dataset_y = []
    with tf.gfile.GFile(source_path, mode="r") as source_file:
        with tf.gfile.GFile(target_path, mode="r") as target_file:
            source, target = source_file.readline(), target_file.readline()
            counter = 0
            while source and target and (not max_size or counter < max_size):
                counter += 1
                if counter % 100000 == 0:
                    print("  reading data line %d" % counter)
                    sys.stdout.flush()
                source_ids = [int(x) for x in source.split()]
                source_ids.append(GO_ID)
                target_ids = [int(x) for x in target.split()]
                target_ids.append(EOS_ID)
                dataset_x.append(np.array(source_ids))
                dataset_y.append(np.array(target_ids))
                source, target = source_file.readline(), target_file.readline()
    return dataset_x, dataset_y


    with open(sentence_file, 'r', encoding='utf-8') as infile_sentence:
        with open(slot_file, 'r', encoding='utf-8') as infile_slot:
            sentence, slot = infile_sentence.readlines(), infile_slot.readlines()
    len_sentence = len(sentence)
    len_slot = len(slot)
    if len_sentence != len_slot:
        raise Exception('Length is not matched!')
    print("Processing line %d" % len_sentence)
    return sentence, slot, len_sentence


def split_data(
      sentence_file,
      slot_file,
      sentence_training_file,
      sentence_developing_file,
      slot_training_file,
      slot_developing_file):
    if not gfile.Exists(sentence_training_file):
        with open(sentence_file, 'r', encoding='utf-8') as infile_sentence:
            with open(slot_file, 'r', encoding='utf-8') as infile_slot:
                sentence, slot = infile_sentence.readlines(), infile_slot.readlines()
        len_sentence = len(sentence)
        len_slot = len(slot)
        if len_sentence != len_slot:
            raise Exception('Length is not matched!')
        print("Processing line %d" % len_sentence)
        num_dev = round(len_sentence/200)
        # Index for random sampling
        idx = random.sample(range(len_sentence), len_sentence)
        sentence_training = [sentence[i] for i in idx[:-num_dev]]
        with open(sentence_training_file, "w") as outfile:
            for line in sentence_training:
                outfile.write(str(line))
        sentence_developing = [sentence[i] for i in idx[-num_dev:]]
        with open(sentence_developing_file, "w") as outfile:
            for line in sentence_developing:
                outfile.write(str(line))
        slot_training = [slot[i] for i in idx[:-num_dev]]
        with open(slot_training_file, "w") as outfile:
            for line in slot_training:
                outfile.write(str(line))
        slot_developing = [slot[i] for i in idx[-num_dev:]]
        with open(slot_developing_file, "w") as outfile:
            for line in slot_developing:
                outfile.write(str(line))


def prepare_data(data_dir, from_train_path, to_train_path, from_dev_path, to_dev_path, from_vocabulary_size,
                 to_vocabulary_size, tokenizer=None):
    """Preapre all necessary files that are required for the training.

        Args:
            data_dir: directory in which the data sets will be stored.
            from_train_path: path to the file that includes "from" training samples.
            to_train_path: path to the file that includes "to" training samples.
            from_dev_path: path to the file that includes "from" dev samples.
            to_dev_path: path to the file that includes "to" dev samples.
            from_vocabulary_size: size of the "from language" vocabulary to create and use.
            to_vocabulary_size: size of the "to language" vocabulary to create and use.
            tokenizer: a function to use to tokenize each data sentence;
                if None, basic_tokenizer will be used.

        Returns:
            A tuple of 6 elements:
                (1) path to the token-ids for "from language" training data-set,
                (2) path to the token-ids for "to language" training data-set,
                (3) path to the token-ids for "from language" development data-set,
                (4) path to the token-ids for "to language" development data-set,
                (5) path to the "from language" vocabulary file,
                (6) path to the "to language" vocabulary file.
    """
    # Create vocabularies of the appropriate sizes.
    sentence_file = os.path.join(data_dir, "training_sentence.txt")
    slot_file = os.path.join(data_dir, "training_slot.txt")
    if not gfile.Exists(sentence_file) and not gfile.Exists(slot_file):
        import training_data as gen_data
        gen_data.main()
    to_vocab_path = os.path.join(data_dir, "vocab%d.slot" % to_vocabulary_size)
    split_data(sentence_file, slot_file, from_train_path,
               from_dev_path, to_train_path, to_dev_path) # If no data set pairs
    from_vocab_path = os.path.join(data_dir, "vocab%d.sentence" % from_vocabulary_size)
    create_vocabulary(to_vocab_path, to_train_path, to_vocabulary_size, tokenizer)
    create_vocabulary(from_vocab_path, from_train_path, from_vocabulary_size, tokenizer)

    # Create token ids for the training data.
    to_train_ids_path = to_train_path + (".ids%d" % to_vocabulary_size)
    from_train_ids_path = from_train_path + (".ids%d" % from_vocabulary_size)
    data_to_token_ids(to_train_path, to_train_ids_path, to_vocab_path, tokenizer)
    data_to_token_ids(from_train_path, from_train_ids_path, from_vocab_path, tokenizer)

    # Create token ids for the development data.
    to_dev_ids_path = to_dev_path + (".ids%d" % to_vocabulary_size)
    from_dev_ids_path = from_dev_path + (".ids%d" % from_vocabulary_size)
    data_to_token_ids(to_dev_path, to_dev_ids_path, to_vocab_path, tokenizer)
    data_to_token_ids(from_dev_path, from_dev_ids_path, from_vocab_path, tokenizer)

    return (from_train_ids_path, to_train_ids_path,
            from_dev_ids_path, to_dev_ids_path,
            from_vocab_path, to_vocab_path)
