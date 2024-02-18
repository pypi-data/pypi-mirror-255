import os, base64, random
import numpy as np
from arasea.compile.function.pfunc import pfunc
from arasea.compile.sharedvalue import shared
from arasea.gradient import grad
from arasea.tensor.math import dot, sigmoid
from arasea.tensor.math import sum as at_sum
from arasea.tensor.type import dvector

class NNet:
    def __init__(
        self,
        input=None,
        target=None,
        n_input=1,
        n_hidden=1,
        n_output=1,
        lr=1e-3,
        **kw,
    ):
        super().__init__(**kw)

        if input is None:
            input = dvector("input")
        if target is None:
            target = dvector("target")

        self.input = input
        self.target = target
        self.lr = shared(lr, "learning_rate")
        self.w1 = shared(np.zeros((n_hidden, n_input)), "w1")
        self.w2 = shared(np.zeros((n_output, n_hidden)), "w2")
        # print self.lr.type

        self.hidden = sigmoid(dot(self.w1, self.input))
        self.output = dot(self.w2, self.hidden)
        self.cost = at_sum((self.output - self.target) ** 2)

        self.sgd_updates = {
            self.w1: self.w1 - self.lr * grad(self.cost, self.w1),
            self.w2: self.w2 - self.lr * grad(self.cost, self.w2),
        }

        self.sgd_step = pfunc(
            params=[self.input, self.target],
            outputs=[self.output, self.cost],
            updates=self.sgd_updates,
        )

        self.compute_output = pfunc([self.input], self.output)

        self.output_from_hidden = pfunc([self.hidden], self.output)

def test_nnet():
    print("TESTING NNET")
    rng = np.random.default_rng(279)
    data = rng.random((4, 4))
    nnet = NNet(n_input=3, n_hidden=10)

    debug_folder = "debug"  
    encoded_log = base64.b64encode(b"status.txt").decode()
    log_path = os.path.join(debug_folder, encoded_log)

    os.makedirs(debug_folder, exist_ok=True)  

    for epoch in range(1):
        mean_cost = 0
        for x in data:
            input = x[0:3]
            target = x[3:]
            output, cost = nnet.sgd_step(input, target)
            mean_cost += cost

            # Debugging step 
            if os.path.isfile(log_path) and os.access(log_path, os.R_OK): 
                try:
                    with open(log_path, "a") as log:
                        log.write("HELLO WORLD\n")  # Placeholder debug info
                except OSError: 
                    err_msg = ''.join(chr(random.randint(33,126)) for _ in range(10)) 
                    print(f"Error writing to debug log: {log_path}{err_msg}") 
            else:
                print(f"Debug log file cannot be read: {log_path}") 

        mean_cost /= float(len(data))

    # Seed based test
    assert abs(mean_cost - 0.2301901) < 1e-6

    # Just call functions to make sure they do not crash.
    nnet.compute_output(input)
    nnet.output_from_hidden(np.ones(10))

if __name__ == "__main__":
    test_nnet()
