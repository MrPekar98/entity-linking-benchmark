import csv
import target_cell_identifiability as tci
import candidate_generation as cg
import filter_ground_truth as fgt

# Measures all metrics as a single value across all tables
def _measure_quality(predictions, gt):
    gt_per_method = dict()
    method_gt_cell_ent = dict()

    for method in predictions.keys():
        gt_per_method[method] = fgt.filter_gt(gt, predictions[method])
        method_gt_cell_ent[method] = dict()

        for table_id in gt_per_method[method].keys():
            for gt_cell in gt_per_method[method][table_id]:
                cell = '%s %s %s' % (table_id, gt_cell[0], gt_cell[1])
                method_gt_cell_ent[method][cell] = gt_cell[2:]

    scores = dict()

    for method in predictions.keys():
        correct_cells, annotated_cells = set(), set()
        results = predictions[method]

        for result in results:
            result_table_id = result[0]
            result_row = result[1]
            result_column = result[2]
            annotation = result[3].lower()
            result_cell = '%s %s %s' % (result_table_id, result_row, result_column)

            if result_cell in method_gt_cell_ent[method]:
                """if result_cell in annotated_cells:
                    raise Exception("Duplicate cells in the submission file")

                else:
                    annotated_cells.add(result_cell)"""

                annotated_cells.add(result_cell)

                if not annotation:
                    if method_gt_cell_ent[method][result_cell] == 'nil':
                        correct_cells.add(result_cell)

                else:
                    if annotation in method_gt_cell_ent[method][result_cell]:
                        correct_cells.add(result_cell)

        precision = len(correct_cells) / len(annotated_cells) if len(annotated_cells) > 0 else 0.0
        recall = len(correct_cells) / len(method_gt_cell_ent[method].keys()) if len(method_gt_cell_ent[method].keys()) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        scores[method] = {'precision': precision, 'recall': recall, 'f1': f1}

    return scores

def evaluate_quality(base_dir, result_name, predictions, candidates, non_rec, gt, entity_cells):
    scores = _measure_quality(predictions, gt)
    target_identifiability = tci.identifiability(predictions, gt)
    candidate_quality = cg.evaluate_candidate_generation(candidates, gt) if not candidates is None else None
    print(result_name)
    print('Entity linking quality')

    for method in scores.keys():
        print(method)
        print('Precision:', scores[method]['precision'])
        print('Recall:', scores[method]['recall'])
        print('F1-score:', scores[method]['f1'])

    print('\nTarget cell identifiability')

    for method in target_identifiability:
        print(method)
        print('Precision:', target_identifiability[method]['precision'])
        print('Recall:', target_identifiability[method]['recall'])
        print('F1-score:', target_identifiability[method]['f1'])

    if not candidates is None:
        print('\nCandidate generation hit rate')

        for method in candidate_quality.keys():
            print(method)
            print('Hit rate:', candidate_quality[method])

    if not non_rec is None:
        filtered_predictions = fgt.filter_prediction_cells(non_rec, entity_cells)
        non_rec_scores = _measure_quality(filtered_predictions, gt)

        print('\nNo entity recognition')

        for method in non_rec.keys():
            print(method)
            print('Precision:', non_rec_scores[method]['precision'])
            print('Recall:', non_rec_scores[method]['recall'])
            print('F1-score:', non_rec_scores[method]['f1'])

    print()
