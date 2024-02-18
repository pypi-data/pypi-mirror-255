import numpy as np
import logging
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.disable_v2_behavior()


# initial varphi for rgb input
init_varphi = np.asarray([[0.294, 0.110, 0.894],
                          [0.750, 0.088, 0.425]])

# # initial varphi for bgr input
# init_varphi = np.asarray([[0.6060, 1.2680, 0.7989],
#                           [1.2383, 1.2540, 0.3927]])


class AdaptiveColorDeconvolution():
    
    def __init__(self, pixel_number, step=300, batch_size=1500):
        # TODO : what is pixel number, is it related to the input
        super().__init__()
        self._pn = pixel_number
        self._bs = batch_size
        self._step_per_epoch = int(pixel_number / batch_size)
        self._epoch = int(step / self._step_per_epoch)
        self._template_dc_mat = None
        self._template_w_mat = None
        
    
    def fit(self, images):
        opt_cd_mat, opt_w_mat = self.extract_adaptive_cd_params(images)
        self._template_dc_mat = opt_cd_mat
        self._template_w_mat = opt_w_mat
        
    
    def transform(self, images):
        if self._template_dc_mat is None:
            raise AssertionError('Run fit function first.')

        opt_cd_mat, opt_w_mat = self.extract_adaptive_cd_params(images)
        transform_mat = np.matmul(opt_cd_mat * opt_w_mat,
                                  np.linalg.inv(self._template_dc_mat * self._template_w_mat))

        od = -np.log((np.asarray(images, float) + 1) / 256.0)
        normed_od = np.matmul(od, transform_mat)
        normed_images = np.exp(-normed_od) * 256 - 1

        return np.maximum(np.minimum(normed_images, 255), 0)
    
    def he_decomposition(self, images, od_output=True):
        if self._template_dc_mat is None:
            raise AssertionError('Run fit function first.')

        opt_cd_mat, _ = self.extract_adaptive_cd_params(images)

        od = -np.log((np.asarray(images, float) + 1) / 256.0)
        normed_od = np.matmul(od, opt_cd_mat)

        if od_output:
            return normed_od
        else:
            normed_images = np.exp(-normed_od) * 256 - 1
            return np.maximum(np.minimum(normed_images, 255), 0)


    def sampling_data(self, images):
        pixels = np.reshape(images, (-1, 3))
        pixels = pixels[np.random.choice(pixels.shape[0], min(self._pn * 20, pixels.shape[0]))]
        od = -np.log((np.asarray(pixels, float) + 1) / 256.0)
        
        # filter the background pixels (white or black)
        tmp = np.mean(od, axis=1)
        od = od[(tmp > 0.3) & (tmp < -np.log(30 / 256))]
        od = od[np.random.choice(od.shape[0], min(self._pn, od.shape[0]))]

        return od

    def extract_adaptive_cd_params(self, images):
        """
        :param images: RGB uint8 format in shape of [k, m, n, 3], where
                       k is the number of ROIs sampled from a WSI, [m, n] is 
                       the size of ROI.
        """
        od_data = self.sampling_data(images)
        input_od = tf.placeholder(dtype=tf.float32, shape=[None, 3])
        target, cd, w = self.acd_model(input_od)
        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)
            for ep in range(self._epoch):
                for step in range(self._step_per_epoch):
                    sess.run(target, {input_od: od_data[step * self._bs:(step + 1) * self._bs]})
            opt_cd = sess.run(cd)
            opt_w = sess.run(w)
        return opt_cd, opt_w
    
    
    def acd_model(self, input_od, lambda_p=0.002, lambda_b=10, lambda_e=1, eta=0.6, gamma=0.5):
        """
        Stain matrix estimation by
        "Yushan Zheng, et al., Adaptive Color Deconvolution for Histological WSI Normalization."

        """
        alpha = tf.Variable(init_varphi[0], dtype='float32')
        beta = tf.Variable(init_varphi[1], dtype='float32')
        w = [tf.Variable(1.0, dtype='float32'), tf.Variable(1.0, dtype='float32'), tf.constant(1.0)]

        sca_mat = tf.stack((tf.cos(alpha) * tf.sin(beta), tf.cos(alpha) * tf.cos(beta), tf.sin(alpha)), axis=1)
        cd_mat = tf.matrix_inverse(sca_mat)

        s = tf.matmul(input_od, cd_mat) * w
        h, e, b = tf.split(s, (1, 1, 1), axis=1)

        l_p1 = tf.reduce_mean(tf.square(b))
        l_p2 = tf.reduce_mean(2 * h * e / (tf.square(h) + tf.square(e)))
        l_b = tf.square((1 - eta) * tf.reduce_mean(h) - eta * tf.reduce_mean(e))
        l_e = tf.square(gamma - tf.reduce_mean(s))

        objective = l_p1 + lambda_p * l_p2 + lambda_b * l_b + lambda_e * l_e
        target = tf.train.AdagradOptimizer(learning_rate=0.05).minimize(objective)

        return target, cd_mat, w