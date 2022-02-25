# coding=utf-8
# sys.path.insert(0, 'D:/BKU/LVTN/CODE/real-estate-chatbot/real-estate-extraction')
import pickle
import numpy as np

from data_utils import constants, get_chunks, transform_data
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()


def get_model_api():
    with open('word_tokenizer.pkl', 'rb') as file:
        word_tokenizer = pickle.load(file)
    with open('char_tokenizer.pkl', 'rb') as file:
        char_tokenizer = pickle.load(file)

    sess = tf.Session()
    meta_graph_def = tf.saved_model.loader.load(
        sess,
        [tf.saved_model.tag_constants.SERVING],
        'saved_model'
    )
    signature = meta_graph_def.signature_def
    word_ids = sess.graph.get_tensor_by_name(
        signature['sequence_tags'].inputs['word_ids'].name)
    char_ids = sess.graph.get_tensor_by_name(
        signature['sequence_tags'].inputs['char_ids'].name)
    sequence_length = sess.graph.get_tensor_by_name(
        signature['sequence_tags'].inputs['sequence_length'].name)
    word_length = sess.graph.get_tensor_by_name(
        signature['sequence_tags'].inputs['word_length'].name)
    decode_tags = sess.graph.get_tensor_by_name(
        signature['sequence_tags'].outputs['decode_tags'].name)
    best_scores = sess.graph.get_tensor_by_name(
        signature['sequence_tags'].outputs['best_scores'].name)

    def predict(texts):
        transformed = [
            transform_data.transform_data(text, word_tokenizer, char_tokenizer) for text in texts
        ]
        seq_len = [x[1] for x in transformed]
        words = [x[0] for x in transformed]
        chars = [x[2] for x in transformed]
        word_lengths = transform_data.pad_sequences(
            [x[3] for x in transformed], max(seq_len))
        max_char_len = np.max(word_lengths)
        padded_chars = np.zeros([len(texts), max(seq_len), max_char_len])
        for p1, c1 in zip(padded_chars, chars):
            for i, c2 in enumerate(c1):
                p1[i][:len(c2)] = c2
        feed_dict = {
            word_ids: transform_data.pad_sequences(words, max(seq_len)),
            sequence_length: seq_len,
            char_ids: padded_chars,
            word_length: word_lengths
        }
        predicted = sess.run([decode_tags, best_scores], feed_dict=feed_dict)
        origin_words = (x[4] for x in transformed)
        return [
            {
                "tags": [
                    {
                        "content": " ".join(x[0][s:e]),
                        "type":constants.REVERSE_TAGS[t]
                    } for t, s, e in get_chunks.get_chunks(x[1], constants.CLASSES)
                ],
                "score": float(x[2])
            }
            for x in zip(origin_words, predicted[0], predicted[1])
        ]
    return predict


if __name__ == "__main__":
    texts = [
    	# "Mua nhà mặt tiền đường Võ Văn Tần tiện kinh doanh",
        # "Mình có nhu cầu mua nhà mặt tiền đường Võ Văn Tần tiện kinh doanh",
        "Mình cần thuê nhà 1 trệt 1 lầu có phòng ngủ và PK đường Nguyễn Đình Chiểu"
    ]
    for v in get_model_api()(texts):
        print(v)