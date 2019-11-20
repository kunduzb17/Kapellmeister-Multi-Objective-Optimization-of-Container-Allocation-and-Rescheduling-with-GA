import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.special import binom


class Solution:
    '''
    One instance of a problem solution
    '''
    def __init__(self, value):
        self.value = value
        self.dominates = []
        self.dominated_cardinal = 0
        self.rank = None


def fast_non_dominated_sort(population):
    '''
    Accepts a list of Solutions, for each solution instance
    modifies its rank according to the sorting result.

    Returns list of fronts, each of which is a list of
    solutions. fronts[0] is the nondominated front.
    '''

    fronts = []
    fronts.append([])

    '''
    For each solution, assign a list of solutions it dominates
    to 'dominates' field. Assign a number of solutions that
    dominate it to 'dominated_cardinal' field.
    '''
    for p in population:
        for q in population:
            domination = dominates(p,q)
            if domination == 1:
                p.dominates.append(q)
            elif domination == -1:
                p.dominated_cardinal += 1
        if p.dominated_cardinal == 0:
            p.rank = 1
            fronts[0].append(p)

    '''
    Peel fronts one by one, from nondominated to
    the worst one.
    '''
    i = 0
    while len(fronts[i]) != 0:
        next_front = []
        for p in fronts[i]:
            for q in p.dominates:
                q.dominated_cardinal -= 1
                if q.dominated_cardinal == 0:
                    q.rank = i + 2
                    next_front.append(q)
        i += 1
        fronts.append(next_front)

    fronts.pop()
    return fronts


def dominates(p,q):
    '''
    Returns 1 if p dominates q, -1
    if q dominates p, 0 otherwise.
    '''
    if p.value[0] >= q.value[0] and p.value[1] >= q.value[1]:
        return 1
    elif p.value[0] <= q.value[0] and p.value[1] <= q.value[1]:
        return -1
    else:
        return 0


def get_reference_coords(div, dim):
    '''
    Generates a list of coordinates that divide each
    goal axis by specified number of divisions.
    TODO: Extend to more then two axes.
    '''

    start_vector = np.ones((div+1,))
    start_vector[:div] = np.arange(0,1,1/div)
    coords = np.array([(i,j) for i,j in zip(start_vector, reversed(start_vector))])

    for i in range(3,dim+1):
        coords_update = np.zeros((int(binom(i + div - 1, div)),i))
        reduction_vector = np.zeros((coords.shape[1],))
        reduction_vector[-1] = 1
        offset = 0
        for j in range(div + 1):
            reduced_coords = coords - reduction_vector * j * 1/div
            erase = np.argwhere(reduced_coords < -0.0000001)[:,0]
            reduced_coords = np.delete(reduced_coords, erase, axis=0)
            h, w = reduced_coords.shape
            coords_update[offset:offset+h,:i-1] = reduced_coords
            coords_update[offset:offset+h,i-1] = j*1/div
            offset += h
        coords = coords_update

    return coords


def normalize(candidate_scores, nondom_scores):
    '''
    Normalizes scores if candidate solutions according
    to NSGA-III specification.
    '''

    '''
    This fragment is almost entirely copied from
    official implementation by Deb and his students
    since the paper itself is not very clear on this calculation.

    It basically finds solutions that are closest to each axis
    among nondominated solutions. Resulting points are saved as
    'maximum' points.
    '''

    ideal_point = np.min(candidate_scores, axis=0)
    weights = np.eye(candidate_scores.shape[1])
    weights[weights==0] = 1e6

    asf = np.max(nondom_scores * weights[:,None,:], axis=2)
    I = np.argmin(asf, axis=1)

    maximum = nondom_scores[I,:]

    '''
    Find intercepts of a hyper plane generated by 'maximum'
    points.
    '''
    points = maximum - ideal_point
    b = np.ones(points.shape[1])
    plane = np.linalg.solve(points, b)
    intercepts = 1/plane

    return (candidate_scores - ideal_point)/intercepts

def associate(reference_points, candidate_scores):
    '''
    Associates each candidate with a closest line generated
    by a reference point.

    Outputs two arrays:
    'assoc_table' has the same number of rows as candidate_scores,
        its first column contains reference point index and second - 
        distance to the line generated by it.
    'ref_count' is a 1D array of same length as reference_points.
        For each ref point it contains the number of associated
        solutions.
    '''

    dist_matrix = np.zeros((candidate_scores.shape[0], reference_points.shape[0]))
    ref_count = np.zeros(reference_points.shape[0])

    '''
    Calculate distance from each solution to each line.
    TODO: Reimplement in C or Go
    '''
    for i, c in enumerate(candidate_scores):
        for j, p in enumerate(reference_points):
            diff_vector = c - p.dot(c) * p/np.sum(p**2)
            dist_matrix[i,j] = np.sqrt(np.sum(diff_vector**2))

    assoc_table = np.zeros((candidate_scores.shape[0], 2))
    assoc_table[:,0] = np.argmin(dist_matrix, axis=1)
    assoc_table[:,1] = np.min(dist_matrix, axis=1)

    for a in assoc_table:
        ref_count[np.int(a[0])] += 1

    return assoc_table, ref_count

def visualize_ranks(population, figname):
    for s in population:
        color = 'm'
        if s.rank != None:
            if s.rank % 3 == 1:
                color = 'r'
            elif s.rank % 3 == 2:
                color = 'g'
            else:
                color = 'b'
        plt.scatter(*s.value, c=color)
    plt.savefig(figname)

if __name__ == '__main__':
    '''
    Prepare initial population
    '''
    popsize = 20

    '''
    Give some concrete values to solutions for testing
    purpouses
    '''
    #values = np.random.random_sample((popsize,2))
    initial_coords = np.array([[0.47211927, 0.98787129],
                       [0.94094343, 0.7684067 ],
                       [0.70284234, 0.91674066],
                       [0.21146251, 0.60112486],
                       [0.04835416, 0.89512353],
                       [0.31512954, 0.48553947],
                       [0.52879547, 0.27766949],
                       [0.96938697, 0.750783  ],
                       [0.12147045, 0.38973397],
                       [0.20875761, 0.6897253 ],
                       [0.60568495, 0.24796033],
                       [0.15599147, 0.95841993],
                       [0.26278643, 0.1886119 ],
                       [0.97070001, 0.36794984],
                       [0.91044592, 0.71886261],
                       [0.52536064, 0.58637707],
                       [0.58728183, 0.99748163],
                       [0.13788234, 0.23183102],
                       [0.86295771, 0.84656466],
                       [0.05840085, 0.45842131]])

    initial_population = []
    for c in initial_coords:
        initial_population.append(Solution(c))

    visualize_ranks(initial_population, '1_initial.png')

    '''
    Perform nondominated sort
    '''
    fronts = fast_non_dominated_sort(initial_population)
    nondom = fronts[0]
    visualize_ranks(initial_population, '2_ranked.png')

    '''
    Make a set of candidates that will compete for the
    next generation
    '''
    candidates = []
    cutoff_number = popsize // 2
    candidates_number = 0

    for f in fronts:
        if candidates_number + len(f) < cutoff_number:
            candidates = candidates + f
            candidates_number += len(f)
        elif candidates_number + len(f) == cutoff_number:
            '''
            TODO: implement this when genetic loop is developed
            '''
            print('No need to perform selection!')
        else:
            points_to_choose_number = cutoff_number - len(candidates)
            candidates = candidates + f
            candidates_number += len(f)
            last_front = f
            break
    '''
    'candidates_number' - the amount of solutions that compete for
    next generation
    'candidates' - these solutions len(candidates) = candidates_number
    'last_front' - the front that should be pruned
    '''


    '''
    Generate reference points
    '''
    dimensions = 2
    divisions = 4
    reference_points = get_reference_coords(divisions, dimensions)

    '''
    Visualize the reference points
    '''
    if dimensions == 2:
        fig = plt.figure()
        plt.scatter(reference_points[:,0], reference_points[:,1])
        plt.savefig('3_references.png')
    elif dimensions == 3:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev=10., azim=30)
        ax.scatter(reference_points[:,0], reference_points[:,1], reference_points[:,2])
        plt.savefig('3_references.png')

    '''
    Normalize candidate scores
    '''
    candidate_scores = np.array([s.value for s in candidates])
    nondom_scores = np.array([s.value for s in nondom])

    normalized_candidate_scores = normalize(candidate_scores, nondom_scores)

    '''
    Visualize normalized candidate scores with reference points
    '''
    if dimensions == 2:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(-0.1,1.1)
        ax.set_ylim(-0.1,1.1)
        ax.scatter(normalized_candidate_scores[:,0],normalized_candidate_scores[:,1])

        for r in reference_points:
            x, y = r
            if x > y:
                ax.plot((0,1), (0,y/x), 'r-')
            elif y > x:
                ax.plot((0,x/y), (0,1), 'r-')
            else:
                ax.plot((0,1), (0,1), 'r-')

        plt.savefig('4_normalized.png')


