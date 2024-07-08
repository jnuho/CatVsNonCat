package pkg

func BinarySearch(arr []int, target int) int {
	if len(arr) <= 0 {
		return -1
	}

	L := 0
	R := len(arr) - 1

	for L <= R {
		median := (L + R) / 2

		if arr[median] == target {
			return median
		} else if arr[median] > target {
			R = median - 1
		} else {
			L = median + 1
		}
	}

	return -1
}

// func main() {
// 	arr := []int{1, 2, 9, 20, 31, 45, 63, 70, 100}
// 	fmt.Println(BinarySearch(arr, 63))
// }
