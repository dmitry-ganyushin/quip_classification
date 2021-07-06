import sys
import numpy as np
import adios2

APS = 100

PatchesFileName = sys.argv[1][0:-1]
BatchesFileName = sys.argv[2][0:-1]

BatchSize = int(sys.argv[3])

print('BatchSize = ', BatchSize)


def whiteness(png):
    wh = (np.std(png[:, :, 0].flatten()) + np.std(png[:, :, 1].flatten()) + np.std(png[:, :, 2].flatten())) / 3.0
    return wh


def load_data(todo_list, rind):
    X = np.zeros(shape=(BatchSize * 40, 3, APS, APS), dtype=np.float32)
    inds = np.zeros(shape=(BatchSize * 40,), dtype=np.int32)
    coor = np.zeros(shape=(20000000, 2), dtype=np.int32)

    xind = 0
    lind = 0
    cind = 0

    with adios2.open(PatchesFileName, "r") as fh:
        for fstep in fh:
            step = fstep.current_step()
            # inspect variables in current step
            step_vars = fstep.available_variables()
            if step == 0:
                for fn in todo_list:
                    lind += 1
                    if len(fn.split('_')) < 4:
                        continue

                    x_off = float(fn.split('_')[0])
                    y_off = float(fn.split('_')[1])
                    svs_pw = float(fn.split('_')[2])
                    png_pw = float(fn.split('_')[3].split('.png')[0])
                    var = step_vars[fn]
                    nx = int(var["Shape"].split(",")[0].strip())
                    ny = int(var["Shape"].split(",")[1].strip())
                    print("processing : {} nx = {}  ny = {}".format(fn, nx, ny))
                    start = [0, 0, 0]
                    count = [nx, ny, 3]
                    image = fstep.read(fn, start, count)
                    png = np.array(image)
                    for x in range(0, png.shape[1], APS):
                        if x + APS > png.shape[1]:
                            continue
                        for y in range(0, png.shape[0], APS):
                            if y + APS > png.shape[0]:
                                continue

                            if whiteness(png[y:y + APS, x:x + APS, :]) >= 12:
                                X[xind, :, :, :] = png[y:y + APS, x:x + APS, :].transpose()
                                inds[xind] = rind
                                xind += 1

                            coor[cind, 0] = np.int32(x_off + (x + APS / 2) * svs_pw / png_pw)
                            coor[cind, 1] = np.int32(y_off + (y + APS / 2) * svs_pw / png_pw)
                            cind += 1
                            rind += 1
                    if xind >= BatchSize:
                        break
    X = X[0:xind]
    inds = inds[0:xind]
    coor = coor[0:cind]

    return todo_list[lind:], X, inds, coor, rind


def main():
    todo_list = list()
    with adios2.open(PatchesFileName, "r") as fh:
        for fstep in fh:
            vars = fstep.available_variables()
            for name in vars:
                todo_list.append(name)
    with adios2.open(BatchesFileName, "w") as fh:
        rind = 0
        while len(todo_list) > 0:
            todo_list, inputs, inds, coor, rind = load_data(todo_list, rind)
            shape = [inputs.shape[0], inputs.shape[1], inputs.shape[2], inputs.shape[3]]
            start = [0, 0, 0, 0]
            count = [inputs.shape[0], inputs.shape[1], inputs.shape[2], inputs.shape[3]]
            fh.write("inputs", inputs, shape, start, count)
            shape = [inds.shape[0]]
            start = [0]
            count = [inds.shape[0]]
            fh.write("inds", inds, shape, start, count)
            rind_arr = np.zeros(shape=(1,), dtype=np.int32)
            rind_arr[0] = rind
            fh.write("rind", rind_arr)
            shape = [coor.shape[0], coor.shape[1]]
            start = [0, 0]
            count = [coor.shape[0], coor.shape[1]]
            fh.write("coor", coor, shape, start, count, end_step=True)
    #TODODG codes for diagnostics
    return 0

if __name__ == "__main__":
    sys.exit(main())
