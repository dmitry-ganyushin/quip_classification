import getopt
import sys
import os
import numpy as np
from PIL import Image
import time

from external_model import load_external_model, pred_by_external_model

from PIL import ImageFile
NOADIOS = False
try:
    import adios2
except ImportError:
    NOADIOS = True

ImageFile.LOAD_TRUNCATED_IMAGES = True

APS = 100

#TileFolder = sys.argv[1] + '/'
TileFolder = sys.argv[1][0:-1] # remove last /
BPFileName = sys.argv[1][0:-1]
CNNModel = sys.argv[2]

heat_map_out = sys.argv[3]

BatchSize = int(sys.argv[4])  # shahira: Batch size argument
# BatchSize = 96;
# BatchSize = 48;
print('BatchSize = ', BatchSize)


def whiteness(png):
    wh = (np.std(png[:, :, 0].flatten()) + np.std(png[:, :, 1].flatten()) + np.std(png[:, :, 2].flatten())) / 3.0
    return wh

def load_data(needed_step):
    X = np.zeros(shape=(BatchSize * 40, 3, APS, APS), dtype=np.float32)
    inds = np.zeros(shape=(BatchSize * 40,), dtype=np.int32)
    coor = np.zeros(shape=(20000000, 2), dtype=np.int32)
    rind = 0
    with adios2.open(BPFileName + "_patches", "r") as fh:

        for fstep in fh:

            # inspect variables in current step
            # we know what we are looking for
            # step_vars = fstep.available_variables()

            # lenear searh for the needed step
            step = fstep.current_step()
            if( step == needed_step):

                # read variables return a numpy array with corresponding selection
                start = [0,0,0,0]
                count = [X.shape[0], X.shape[1], X.shape[2], X.shape[3]]
                X = fstep.read("inputs", start, count)
                start = [0]
                count = [inds.shape[0]]
                inds = fstep.read("inds", start, count)
                rind = fstep.read("rind")
                start = [0, 0]
                count = [coor.shape[0], coor.shape[1]]
                coor = fstep.write("coor", coor, start, count)

    return X, inds, coor, rind

def _load_data(todo_list, rind, input_type):

    X = np.zeros(shape=(BatchSize * 40, 3, APS, APS), dtype=np.float32)
    inds = np.zeros(shape=(BatchSize * 40,), dtype=np.int32)
    coor = np.zeros(shape=(20000000, 2), dtype=np.int32)

    xind = 0
    lind = 0
    cind = 0
    if input_type == "adios":
        with adios2.open(BPFileName, "r") as fh:
            for fstep in fh:
                step = fstep.current_step()
                # inspect variables in current step
                step_vars = fstep.available_variables()
                if step == 0:
                    for fn in todo_list:
                        lind += 1
                        #full_fn = TileFolder + '/' + fn
                        #if not os.path.isfile(full_fn):
                        #    continue
                        if len(fn.split('_')) < 4:
                           continue

                        x_off = float(fn.split('_')[0])
                        y_off = float(fn.split('_')[1])
                        svs_pw = float(fn.split('_')[2])
                        png_pw = float(fn.split('_')[3].split('.png')[0])
                        #png = np.array(Image.open(full_fn).convert('RGB'))
                        #start, count?
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

                                if (whiteness(png[y:y + APS, x:x + APS, :]) >= 12):
                                    X[xind, :, :, :] = png[y:y + APS, x:x + APS, :].transpose()
                                    inds[xind] = rind
                                    xind += 1

                                coor[cind, 0] = np.int32(x_off + (x + APS / 2) * svs_pw / png_pw)
                                coor[cind, 1] = np.int32(y_off + (y + APS / 2) * svs_pw / png_pw)
                                cind += 1
                                rind += 1
                        if xind >= BatchSize:
                            break
    else:
        for fn in todo_list:
            lind += 1
            full_fn = TileFolder + '/' + fn
            if not os.path.isfile(full_fn):
                continue
            if len(fn.split('_')) < 4:
                continue

            x_off = float(fn.split('_')[0])
            y_off = float(fn.split('_')[1])
            svs_pw = float(fn.split('_')[2])
            png_pw = float(fn.split('_')[3].split('.png')[0])
            png = np.array(Image.open(full_fn).convert('RGB'))
            for x in range(0, png.shape[1], APS):
                if x + APS > png.shape[1]:
                    continue
                for y in range(0, png.shape[0], APS):
                    if y + APS > png.shape[0]:
                        continue

                    if (whiteness(png[y:y + APS, x:x + APS, :]) >= 12):
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


def val_fn_epoch_on_disk(classn, model, input_type):
    all_or = np.zeros(shape=(20000000, classn), dtype=np.float32)
    all_inds = np.zeros(shape=(20000000,), dtype=np.int32)
    all_coor = np.zeros(shape=(20000000, 2), dtype=np.int32)
    rind = 0
    n1 = 0
    n2 = 0
    n3 = 0
    with adios2.open(BPFileName + "_batches", "r") as fh:
        nsteps = fh.steps()

    # shahira: Handling tensorflow memory exhaust issue on large slides
    reset_limit = 100
    cur_indx = 0
    iotime = 0
    todo_list = [ s for s in range(nsteps)]
    while len(todo_list) > 0:
        t0 = time.perf_counter()
        inputs, inds, coor, rind = load_data(todo_list.pop(0))
        iotime = iotime + time.perf_counter() - t0
        if len(inputs) == 0:
            break

        output = pred_by_external_model(model, inputs)

        all_or[n1:n1 + len(output)] = output
        all_inds[n2:n2 + len(inds)] = inds
        all_coor[n3:n3 + len(coor)] = coor
        n1 += len(output)
        n2 += len(inds)
        n3 += len(coor)

        # shahira: Handling tensorflow memory exhaust issue on large slides
        cur_indx += 1
        if (cur_indx > reset_limit):
            cur_indx = 0
            print('Restarting model!')
            model.restart_model()
            print('Restarted!')
    print("IOTime = {} sec for {} batches".format(iotime, nsteps))
    all_or = all_or[:n1]
    all_inds = all_inds[:n2]
    all_coor = all_coor[:n3]
    return all_or, all_inds, all_coor

def _val_fn_epoch_on_disk(classn, model, input_type):
    all_or = np.zeros(shape=(20000000, classn), dtype=np.float32)
    all_inds = np.zeros(shape=(20000000,), dtype=np.int32)
    all_coor = np.zeros(shape=(20000000, 2), dtype=np.int32)
    rind = 0
    n1 = 0
    n2 = 0
    n3 = 0
    if input_type == "adios":
        todo_list = list()
        with adios2.open(BPFileName, "r") as fh:
            for fstep in fh:
                vars = fstep.available_variables()
                for name in vars:
                    todo_list.append(name)
    else:
        todo_list = os.listdir(TileFolder)
    n_files = len(todo_list)
    # shahira: Handling tensorflow memory exhaust issue on large slides
    reset_limit = 100
    cur_indx = 0
    iotime = 0
    while len(todo_list) > 0:
        t0 = time.perf_counter()
        todo_list, inputs, inds, coor, rind = _load_data(todo_list, rind, input_type)
        iotime = iotime + time.perf_counter() - t0
        if len(inputs) == 0:
            break

        output = pred_by_external_model(model, inputs)

        all_or[n1:n1 + len(output)] = output
        all_inds[n2:n2 + len(inds)] = inds
        all_coor[n3:n3 + len(coor)] = coor
        n1 += len(output)
        n2 += len(inds)
        n3 += len(coor)

        # shahira: Handling tensorflow memory exhaust issue on large slides
        cur_indx += 1
        if (cur_indx > reset_limit):
            cur_indx = 0
            print('Restarting model!')
            model.restart_model()
            print('Restarted!')
    print("IOTime = {} sec for {} files".format(iotime, n_files))
    all_or = all_or[:n1]
    all_inds = all_inds[:n2]
    all_coor = all_coor[:n3]
    return all_or, all_inds, all_coor


def split_validation(classn, input_type):
    model = load_external_model(CNNModel)

    # Testing
    Or, inds, coor = val_fn_epoch_on_disk(classn, model, input_type)
    Or_all = np.zeros(shape=(coor.shape[0],), dtype=np.float32)
    Or_all[inds] = Or[:, 0]

    fid = open(TileFolder + '/' + heat_map_out, 'w')
    for idx in range(0, Or_all.shape[0]):
        fid.write('{} {} {}\n'.format(coor[idx][0], coor[idx][1], Or_all[idx]))
    fid.close()

    return


def main(input_type):
    if not os.path.exists(TileFolder):
        exit(0)
    t0 = time.perf_counter()
    classes = ['Lymphocytes']
    classn = len(classes)
    sys.setrecursionlimit(10000)

    split_validation(classn, input_type)
    print('DONE in {} sec'.format(time.perf_counter() -t0 ))

def printUsage():
    print("Options: --input=adios ")
    return

if __name__ == "__main__":
    INPUT_TYPE = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "input"])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            printUsage()
            sys.exit()
        elif opt in ("-i", "--input"):
            INPUT_TYPE = arg
            if INPUT_TYPE == "adios" and NOADIOS:
                print("Cannot import required ADIOS library", file=sys.stderr)
                sys.exit(1)

    main("adios")
