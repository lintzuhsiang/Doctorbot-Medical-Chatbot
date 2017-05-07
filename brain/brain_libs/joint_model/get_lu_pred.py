# -*- coding: utf-8 -*-
"""
Get predicted intent and slot from user utterance.
"""

import tensorflow as tf

import sys
import os
import numpy as np
import jieba
import data_utils
import multi_task_model

tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 16,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 128, "Size of each model layer.")
tf.app.flags.DEFINE_integer("word_embedding_size", 128, "Size of the word embedding")
tf.app.flags.DEFINE_integer("num_layers", 1, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("in_vocab_size", 10000, "max vocab Size.")
tf.app.flags.DEFINE_integer("out_vocab_size", 10000, "max tag vocab Size.")
tf.app.flags.DEFINE_string("data_dir", "../joint_model/data/hospital", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "../joint_model/model_tmp", "Training directory.")
tf.app.flags.DEFINE_boolean("use_attention", True,
                            "Use attention based RNN")
tf.app.flags.DEFINE_integer("max_sequence_length", 30,
                            "Max sequence length.")
tf.app.flags.DEFINE_float("dropout_keep_prob", 0.5,
                          "dropout keep cell input and output prob.")
tf.app.flags.DEFINE_boolean("bidirectional_rnn", True,
                            "Use birectional RNN")
tf.app.flags.DEFINE_string("task", "joint", "Options: joint; intent; tagging")

FLAGS = tf.app.flags.FLAGS

task = dict({'intent':0, 'tagging':0, 'joint':0})
if FLAGS.task == 'intent':
    task['intent'] = 1
elif FLAGS.task == 'tagging':
    task['tagging'] = 1
elif FLAGS.task == 'joint':
    task['intent'] = 1
    task['tagging'] = 1
    task['joint'] = 1

_buckets = [(FLAGS.max_sequence_length, FLAGS.max_sequence_length)]
# Create vocabularies of the appropriate sizes.
vocab_path = os.path.join(FLAGS.data_dir, "in_vocab_%d.txt" % FLAGS.in_vocab_size)
tag_vocab_path = os.path.join(FLAGS.data_dir, "out_vocab_%d.txt" % FLAGS.out_vocab_size)
label_vocab_path = os.path.join(FLAGS.data_dir, "label.txt")

vocab, rev_vocab = data_utils.initialize_vocabulary(vocab_path)
tag_vocab, rev_tag_vocab = data_utils.initialize_vocabulary(tag_vocab_path)
label_vocab, rev_label_vocab = data_utils.initialize_vocabulary(label_vocab_path)

jieba.load_userdict("../data_resource/doctor_dict.txt")
jieba.load_userdict("../data_resource/disease_dict.txt")
jieba.load_userdict("../data_resource/division_dict.txt")
jieba.load_userdict("../data_resource/week_dict.txt")
jieba.load_userdict("../data_resource/other_dict.txt")

_buckets = [(FLAGS.max_sequence_length, FLAGS.max_sequence_length)]
bucket_id = 0


class LuModel(object):
    def __init__(self):
        def create_model(session, source_vocab_size, target_vocab_size, label_vocab_size):
            """Create model and initialize or load parameters in session."""
            with tf.variable_scope("model", reuse=None):
                model_test = multi_task_model.MultiTaskModel(
                        source_vocab_size, target_vocab_size, label_vocab_size, _buckets,
                        FLAGS.word_embedding_size, FLAGS.size, FLAGS.num_layers,
                        FLAGS.max_gradient_norm, FLAGS.batch_size,
                        dropout_keep_prob=FLAGS.dropout_keep_prob, use_lstm=True,
                        forward_only=True,
                        use_attention=FLAGS.use_attention,
                        bidirectional_rnn=FLAGS.bidirectional_rnn,
                        task=task)
            ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
            if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path + ".meta"):
                print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
                model_test.saver.restore(session, ckpt.model_checkpoint_path)
            else:
                print("Pre-trained model did not exist!")
            return model_test

        self.sess = tf.Session()
        self.model_test = create_model(self.sess, len(vocab),
                                       len(tag_vocab), len(label_vocab))
        print('Applying Parameters:')
        for k,v in FLAGS.__dict__['__flags'].items():
            print('%s: %s' % (k, str(v)))
        print("Preparing model in %s" % FLAGS.data_dir)
        if not os.path.exists(FLAGS.data_dir):
            print("%s not exist! Abort!" % FLAGS.data_dir)
            exit
        print("Max sequence length: %d." % _buckets[0][0])
        print("Creating %d layers of %d units." % (FLAGS.num_layers, FLAGS.size))
        print ("Creating model with source_vocab_size=%d, target_vocab_size=%d,\
               and label_vocab_size=%d." % (len(vocab), len(tag_vocab), len(label_vocab)))

    def semantic_frame(self, sentence):
        seg_gen = list(jieba.cut(sentence, cut_all=False))
        _sentence = " ".join(seg_gen)
        # Get token-ids for the input sentence.
        token_ids = data_utils.sentence_to_token_ids(
            _sentence, vocab, data_utils.UNK_ID_dict['with_padding'])
        encoder_inputs, tags, tag_weights, sequence_length, labels = self.model_test.get_one(
            [[[token_ids, [], [0]]]], bucket_id, 0)
        _, step_loss, tagging_logits, classification_logits = self.model_test.joint_step(
            self.sess, encoder_inputs, tags, tag_weights, labels, sequence_length,
            bucket_id, True)
        intent_label = rev_label_vocab[np.argmax(classification_logits[0], 0)]
        slot_list = [rev_tag_vocab[np.argmax(x)] for x in tagging_logits[:sequence_length[0]]]
        slot_dictionary = {'intent': intent_label[1],
                           'slot': {'disease': '', 'division': '', 'doctor': '', 'time': ''}}
        for index, item in enumerate(slot_list):
            if item == 'b-disease':
                slot_dictionary['slot']['disease'] = seg_gen[index]
            elif item == 'b-division':
                slot_dictionary['slot']['division'] = seg_gen[index]
            elif item == 'b-doctor':
                slot_dictionary['slot']['doctor'] = seg_gen[index]
            elif item == 'b-time':
                slot_dictionary['slot']['time'] = seg_gen[index]
        return slot_dictionary

    def get_lu_pred(self, sentence=None):
        if sentence == None:
            # Decode from standard input.
            sys.stdout.write("> ")
            sys.stdout.flush()
            sentence = sys.stdin.readline()
            try:
                while sentence:
                    seg_gen = jieba.cut(sentence, cut_all=False)
                    _sentence = " ".join(seg_gen)
                    # Get token-ids for the input sentence.
                    token_ids = data_utils.sentence_to_token_ids(
                        _sentence, vocab, data_utils.UNK_ID_dict['with_padding'])
                    # Prepare one batch
                    encoder_inputs, tags, tag_weights, sequence_length, labels = self.model_test.get_one(
                        [[[token_ids, [], [0]]]], bucket_id, 0)
                    # Get prediction logits
                    _, step_loss, tagging_logits, classification_logits = self.model_test.joint_step(
                        self.sess, encoder_inputs, tags, tag_weights, labels, sequence_length,
                        bucket_id, True)
                    hyp_label = rev_label_vocab[np.argmax(classification_logits[0],0)]
                    print(hyp_label)
                    hyp_tags = [rev_tag_vocab[np.argmax(x)] for x in tagging_logits[:sequence_length[0]]]
                    print(hyp_tags)
                    print("> ", end="")
                    sys.stdout.flush()
                    sentence = sys.stdin.readline()
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                self.sess.close()
        else:
            seg_gen = jieba.cut(sentence, cut_all=False)
            _sentence = " ".join(seg_gen)
            # Get token-ids for the input sentence.
            token_ids = data_utils.sentence_to_token_ids(
                _sentence, vocab, data_utils.UNK_ID_dict['with_padding'])
            encoder_inputs, tags, tag_weights, sequence_length, labels = self.model_test.get_one(
                [[[token_ids, [], [0]]]], bucket_id, 0)
            _, step_loss, tagging_logits, classification_logits = self.model_test.joint_step(
                self.sess, encoder_inputs, tags, tag_weights, labels, sequence_length,
                bucket_id, True)
            hyp_label = rev_label_vocab[np.argmax(classification_logits[0],0)]
            hyp_tags = [rev_tag_vocab[np.argmax(x)] for x in tagging_logits[:sequence_length[0]]]
            return hyp_label, hyp_tags


def main():
    lu = LuModel()
    lu.get_lu_pred()


if __name__ == '__main__':
    main()
